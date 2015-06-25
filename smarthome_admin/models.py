from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import json
from mqtt_conn import client
# Create your models here.
import inspect
import uuid

STATUSES = (
    (0, "CREATED"),
    (1, "SENT"),
    (2, "ACKNOWLEDGED"),
    (3, "COMPLETE"),

)


def init_choices():
    from control_classes import CONTROL_CLASSES
    choices = []
    for key, _ in CONTROL_CLASSES.iteritems():
        choices.append([key, key])
    return choices


class ControllerCapability(models.Model):
    name = models.CharField(max_length=1024)
    control_class = models.CharField(choices=init_choices(), max_length=1024)
    init_arguments = models.CharField(max_length=4096)
    description = models.TextField()

    def clean(self):
        try:
            obj = json.loads(self.init_arguments)
            cls = self.get_control_class()
            args = inspect.getargspec(cls.init)[0]
            for k in obj.keys():
                if k not in args:
                    raise ValidationError(str(args) + " args are valid")
        except ValueError:
            raise ValidationError("Needs to be valid JSON")

    def get_control_class(self):
        from control_classes import CONTROL_CLASSES
        return CONTROL_CLASSES[self.control_class]

    def init(self, controller):
        self.get_control_class().init(controller, **json.loads(self.init_arguments))

    def incoming_beacon(self, controller):
        self.get_control_class().on_beacon(controller)

    def __unicode__(self):
        return self.name


class ControllerModel(models.Model):
    name = models.CharField(max_length=1024)
    capabilities = models.ManyToManyField(ControllerCapability)

    def init(self, controller):
        for cap in self.capabilities.all():
            cap.init(controller)

    def __unicode__(self):
        return self.name


class SmartHomeController(models.Model):
    name = models.CharField(max_length=1024)
    unique_id = models.CharField(max_length=1024)
    first_registered = models.DateTimeField(auto_now=True)
    model = models.ForeignKey("ControllerModel")
    owner = models.ForeignKey(User, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            ret = super(SmartHomeController, self).save(*args, **kwargs)
            self.model.init(self)
        else:
            ret = super(SmartHomeController, self).save(*args, **kwargs)
        return ret

    def get_topic_name(self):
        return "/smart_plug_work/SmartPlug-%s" % self.unique_id

    def __unicode__(self):
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

    def __unicode__(self):
        return str(self.task_id)


class Socket(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    number = models.SmallIntegerField()
    state = models.BooleanField(default=False)
    human_name = models.TextField()

    def __unicode__(self):
        if self.human_name:
            return self.human_name + str(self.controller)

        return str(self.number) + str(self.controller)

    def send_state(self, toggle=False):
        task = ControllerTask(controller=self.controller)
        task.description = "Toggle Socket"
        if toggle:
            newstate = not self.state
        else:
            newstate = self.state
        task.arguments = json.dumps({"socketnumber": self.number, "state": newstate})
        task.name = "sockettoggle"
        task.save()
        task.send_task()
        self.state = newstate
        self.save()

    def toggle(self):
        self.send_state(True)


















