__author__ = 'dmarkey'
from django.contrib import admin
from models import SmartHomeController, ControllerPing

admin.site.register(SmartHomeController)
admin.site.register(ControllerPing)

