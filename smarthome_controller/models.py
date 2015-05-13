from django.core.exceptions import ValidationError
from django.db import models
import json
import paho.mqtt.publish as publish
# Create your models here.
import inspect
import uuid

STATUSES = (
    (0, "CREATED"),
    (1, "SENT"),
    (2, "ACKNOWLEDGED"),
    (2, "COMPLETE"),

)


def init_choices():
    from controller_init import CONTROLLER_INIT_MAP
    choices = []
    for key, _ in CONTROLLER_INIT_MAP.iteritems():
        choices.append([key, key])
    return choices


class ControllerCapability(models.Model):
    name = models.CharField(max_length=1024)
    init_function = models.CharField(choices=init_choices(), max_length=1024)
    init_arguments = models.CharField(max_length=4096)
    description = models.TextField()

    def clean(self):
        try:
            obj = json.loads(self.init_arguments)
            func = self.get_init_function()
            args = inspect.getargspec(func)[0]
            for k in obj.keys():
                if k not in args:
                    raise ValidationError(str(args) + " args are valid")
        except ValueError:
            raise ValidationError("Needs to be valid JSON")

    def get_init_function(self):
        from controller_init import CONTROLLER_INIT_MAP
        return CONTROLLER_INIT_MAP[self.init_function]


    def init(self, controller):
        self.get_init_function()(controller, **json.loads(self.init_arguments))

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
    unique_id = models.CharField(max_length=1024)
    first_registered = models.DateTimeField(auto_now=True)
    model = models.ForeignKey("ControllerModel")

    def save(self, *args, **kwargs):
        if not self.pk:
            ret = super(SmartHomeController, self).save(*args, **kwargs)
            self.model.init(self)
        else:
            ret = super(SmartHomeController, self).save(*args, **kwargs)
        return ret



    def get_topic_name(self):
        return "/smart_plug_work/SmartPlug-%d" % self.unique_id

    def __unicode__(self):
        return self.unique_id

class ControllerPing(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    time = models.DateTimeField(auto_now=True)


class ControllerTask(models.Model):
    task_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    controller = models.ForeignKey(SmartHomeController)
    description = models.CharField(max_length=4096)
    capability = models.ForeignKey(ControllerCapability)
    arguments = models.CharField(max_length=1024)
    creation_time = models.DateTimeField(auto_now=True)

    status = models.SmallIntegerField(default=0, choices=STATUSES)

    def clean(self):
        try:
            obj = json.loads(self.arguments)

        except ValueError:
            raise ValidationError("Needs to be valid JSON")

    def _get_payload(self):
        message = {}
        message['capability'] = self.capability.name
        message['arguments'] = self.arguments
        message['task_id'] = self.task_id
        return json.dumps(message)


    def send_task(self):
        topic = self.controller.get_topic_name()
        publish.single(topic, self._get_payload(), hostname="dmarkey.com", port=8000)

    def __unicode__(self):
        return str(self.task_id)


class Socket(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    number = models.SmallIntegerField()
    state = models.NullBooleanField()












