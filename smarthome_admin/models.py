from celery import Celery
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import json
#from .mqtt_conn import client
# Create your models here.
import inspect
import uuid
import threading


app = Celery('tasks', broker='amqp://guest@localhost//')


STATUSES = (
    (0, "CREATED"),
    (1, "SENT"),
    (2, "ACKNOWLEDGED"),
    (3, "COMPLETE"),

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

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.unique_id


class ControllerPing(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    time = models.DateTimeField(auto_now=True)
    ip = models.GenericIPAddressField()


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
        return json.dumps(message)

    def send_task(self):
        topic = self.controller.get_topic_name()
        client.publish(topic, self._get_payload(), qos=2)
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

    def __str__(self):
        if self.human_name:
            return self.human_name + str(self.controller)

        return str(self.number) + str(self.controller)

    def send_state(self):
        new_task = ControllerTask(controller=self.controller)
        new_task.description = "Toggle Socket"
        new_task.arguments = json.dumps({"socketnumber": self.number, "state": self.state})
        new_task.name = "sockettoggle"
        new_task.save()
        #task.send_task()

    def save(self, *args, send_state=True, **kwargs):
        if self.pk and send_state is True:
            self.send_state()

        tmp = super(Socket, self).save(*args, **kwargs)
        return tmp

    def toggle(self):
        self.state = not self.state
        self.save()


class SocketControl(models.Model):
    socket = models.ForeignKey(Socket)
    action = models.SmallIntegerField(default=0)
    timer = models.IntegerField(default=0)

    def execute(self):
        if self.action == 0 and self.socket.state is True:
            self.socket.state = False
            self.socket.save()
        elif self.action == 1 and self.socket.state is False:
            self.socket.state = True
            self.socket.save()
        elif self.action == 2:
            self.socket.toggle()
        if self.timer != 0:
            task_id = self.socket.toggle.apply_async(delay=self.timer)
            self.socket.queued_task = task_id
            self.socket.save(send_state=False)
            #threading.Timer(self.timer, self.reverse).start()

    def reverse(self):
        self.socket.toggle()


class TemperatureRecord(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    temperature = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)

"""
class TemperatureAction(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    action = models.SmallIntegerField(default=0)
    template = models.CharField(default='{}')
"""

class RemoteEvent(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    encoding = models.CharField(max_length=256)
    value = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)


class RegisteredRemoteEvent(SocketControl):
    encoding = models.CharField(max_length=256)
    value = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)


