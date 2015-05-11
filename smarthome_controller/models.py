from django.db import models

# Create your models here.

TYPES = (
    (1, "ESP8266"),
)

STATUSES = (
    (0, "CREATED"),
    (1, "SENT"),
    (2, "ACKNOWLEDGED"),
    (2, "COMPLETE"),

)


class ControllerCapability(models.Model):
    name = models.CharField(max_length=1024)
    description = models.TextField()


class SmartHomeController(models.Model):
    unique_id = models.CharField(max_length=1024)
    first_registered = models.DateTimeField(auto_created=True)
    type = models.IntegerField(choices=TYPES)
    capabilities = models.ManyToManyField(ControllerCapability)


class ControllerPing(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    time = models.DateTimeField(auto_created=True)


class ControllerTask(models.Model):
    controller = models.ForeignKey(SmartHomeController)
    description = models.CharField(max_length=4096)
    capability = models.ForeignKey(ControllerCapability)
    arguments = models.CharField(max_length=1024)
    status = models.SmallIntegerField(default=0, choices=STATUSES)










