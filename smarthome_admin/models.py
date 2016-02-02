from datetime import datetime, timedelta

import redis
from celery.contrib.methods import task
from celery.contrib.methods import task_method
from celery.task.control import revoke
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import models
import json
import inspect
import uuid


r = redis.StrictRedis(host='localhost', port=6379, db=0)


STATUSES = (
    (0, "CREATED"),
    (1, "SENT"),
    (2, "ACKNOWLEDGED"),
    (3, "COMPLETE"),

)

SOCKET_ACTIONS = (
    (0, "Socket Off"),
    (1, "Socket On"),
    (2, "Socket Toggle"),

)


def init_choices():
    from .control_classes import CONTROL_CLASSES
    choices = []
    for key, _ in CONTROL_CLASSES.items():
        choices.append([key, key])
    return choices


class ControllerCapability(models.Model):
    name = models.CharField(max_length=1024)
    control_class = models.CharField(choices=init_choices(), max_length=1024)
    init_arguments = models.CharField(max_length=4096)
    description = models.TextField()
    route_name = models.CharField(max_length=128)

    def clean(self):
        try:
            obj = json.loads(self.init_arguments)
            cls = self.get_control_class()
            sig = list(dict(inspect.signature(cls.init).parameters).keys())
            sig.remove("controller")
            for k in obj.keys():
                if k not in sig:
                    raise ValidationError(str(sig) + " args are valid")
        except ValueError:
            raise ValidationError("Needs to be valid JSON")

    def get_control_class(self):
        from .control_classes import CONTROL_CLASSES
        return CONTROL_CLASSES[self.control_class]

    def init(self, controller):
        self.get_control_class().init(controller, **json.loads(self.init_arguments))

    def event(self, controller, event):
        self.get_control_class().event(controller, event)

    def __str__(self):
        return self.name


class ControllerModel(models.Model):
    name = models.CharField(max_length=1024)
    capabilities = models.ManyToManyField(ControllerCapability)

    def init(self, controller):
        for cap in self.capabilities.all():
            cap.init(controller)

    def __str__(self):
        return self.name


class SmartHomeController(models.Model):
    name = models.CharField(max_length=1024)
    unique_id = models.CharField(max_length=1024)
    first_registered = models.DateTimeField(auto_now=True)
    model = models.ForeignKey("ControllerModel")
    admin = models.ForeignKey(User, null=True, blank=True)
    users = models.ManyToManyField(User, related_name="controller_users", blank=True)
    human_name = models.TextField(default="No name")
    ip = models.GenericIPAddressField(default="127.0.0.1")
    extra = JSONField(default={})

    def send_message(self, obj):
        obj['controller_id'] = self.unique_id
        return r.publish("/controllers/" + str(self.unique_id), json.dumps(obj))

    def queue_next_task(self):
        if not ControllerTask.objects.filter(status=1, controller=self):
            pending = ControllerTask.objects.filter(status=0, controller=self)
            if pending:
                pending[0].send_task()

    def clear_tasks(self):
        ControllerTask.objects.filter(controller=self).delete()

    def save(self, *args, **kwargs):
        if not self.pk:
            ret = super(SmartHomeController, self).save(*args, **kwargs)
            self.model.init(self)
        else:
            ret = super(SmartHomeController, self).save(*args, **kwargs)
        return ret

    def capabilities(self):
        return self.model.capabilities.all().values()

    def sockets(self):
        return self.socket_set.all().values()

    def get_topic_name(self):
        return "/smart_plug_work/SmartPlug-%s" % self.unique_id

    def extra_items(self):
        return {c.name: c.get_control_class().get_extra_items(self) for c in self.model.capabilities.all()}

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.unique_id


class ControllerTask(models.Model):
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    controller = models.ForeignKey(SmartHomeController)
    description = models.CharField(max_length=4096)
    name = models.CharField(max_length=1024)
    arguments = models.CharField(max_length=1024)
    creation_time = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField(default=0, choices=STATUSES)

    def clean(self):
        try:
            obj = json.loads(self.arguments)
        except ValueError:
            raise ValidationError("Needs to be valid JSON")

    def _get_payload(self):
        message = json.loads(self.arguments)
        message['name'] = self.name
        message['task_id'] = str(self.task_id)
        return message

    def send_task(self):
        self.controller.send_message(self._get_payload())
        self.status = 1
        self.save()

    def save(self, *args, **kwargs):

        ret_temp = super(ControllerTask, self).save(*args, **kwargs)
        if self.status == 0:
            self.controller.queue_next_task()
        return ret_temp

    def __str__(self):
        return str(self.task_id)


class Socket(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    number = models.SmallIntegerField()
    state = models.BooleanField(default=False)
    human_name = models.TextField()
    admin = models.ForeignKey(User, null=True, blank=True)
    users = models.ManyToManyField(User, related_name="socket_users", blank=True)
    queued_task = models.UUIDField(null=True, blank=True)
    extra = JSONField(default={})

    def __str__(self):
        if self.human_name:
            return str(self.controller) + " " + self.human_name

        return str(self.controller) + " " + str(self.number)

    def send_state(self):
        new_task = ControllerTask(controller=self.controller)
        new_task.description = "Toggle Socket"
        new_task.arguments = json.dumps({"socketnumber": self.number, "state": self.state})
        new_task.name = "sockettoggle"
        new_task.save()
        # new_task.send_task()

    def save(self, *args, send_state=True, **kwargs):
        if self.pk and send_state is True:
            self.send_state()

        tmp = super(Socket, self).save(*args, **kwargs)
        return tmp

    @task(filter=task_method)
    def toggle(self):
        self.state = not self.state
        self.save()


class SocketSet(models.Model):
    name = models.TextField()
    creator = models.ForeignKey("auth.User")
    sockets = models.ManyToManyField(Socket)

    def __str__(self):
        return self.name


class SocketControl(models.Model):
    socket_set = models.ForeignKey(SocketSet, null=True)
    action = models.SmallIntegerField(default=0, choices=SOCKET_ACTIONS)
    timer = models.IntegerField(default=0)
    creator = models.ForeignKey("auth.User", null=True)

    @task
    def execute(self):

        for socket in self.socket_set.sockets.all():
            if socket.queued_task:
                revoke(str(socket.queued_task))
                socket.queued_task = None
            if self.action == 0 and socket.state is True:
                socket.state = False
                socket.save()
            elif self.action == 1 and socket.state is False:
                socket.state = True
                socket.save()
            elif self.action == 2:
                socket.toggle()
            if self.timer != 0:
                task = socket.toggle.apply_async(countdown=self.timer)
                socket.queued_task = task.task_id
                socket.save(send_state=False)

            # threading.Timer(self.timer, self.reverse).start()


class TemperatureZone(models.Model):
    name = models.TextField(max_length=256)
    controller = models.ForeignKey(SmartHomeController)
    extra = JSONField(default={})

    def get_latest_record(self):
        value = r.hget("zone_latest", str(self.id))
        if value is None:
            return None
        return list(serializers.deserialize('json', value))[0].temperature

    def __str__(self):
        return str(self.controller) + "\\" + self.name


class TemperatureRecord(models.Model):
    temperature = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)
    extra = JSONField(default={})
    zone = models.ForeignKey(TemperatureZone, null=True)

    def save(self, *args, **kwargs):
        ret = super(TemperatureRecord, self).save(*args, **kwargs)
        record = serializers.serialize('json', [self, ])
        r.hset("zone_latest", str(self.zone_id), record)
        return ret

    class Meta:
        ordering = ['-time']


class RemoteEvent(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    encoding = models.CharField(max_length=256)
    value = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)


class RegisteredRemoteEvent(SocketControl):
    encoding = models.CharField(max_length=256)
    value = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)


class SocketTimerSlot(SocketControl):
    enabled = models.BooleanField(default=False)
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)
    start_time = models.TimeField()
    stop_time = models.TimeField()

    def get_days(self):
        return [x for x in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'
                            ] if getattr(self, x)]

    def get_schedule(self):
        return "Between " + str(self.start_time) + " and " + str(self.stop_time) + " on days " + str(self.get_days())

    def save(self, *args, **kwargs):
        if self.start_time > self.stop_time:
            date_one = datetime.now().date()
            date_two = date_one + timedelta(days=1)
            date_one = datetime.combine(date_two, self.stop_time)
            date_two = datetime.combine(date_two, self.start_time)
        else:
            date_one = datetime.combine(datetime.now().date(), self.start_time)
            date_two = datetime.combine(datetime.now().date(), self.stop_time)

        self.timer = (date_two - date_one).total_seconds()

        super(SocketTimerSlot, self).save(*args, **kwargs)

    def countdown(self):
        now = datetime.now().date()
        now_dt = datetime.combine(now, self.start_time)
        self.execute.apply_async(eta=now_dt)
