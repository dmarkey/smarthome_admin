__author__ = 'dmarkey'
from django.contrib import admin
from models import SmartHomeController, ControllerPing, ControllerTask, ControllerCapability, ControllerModel


class SmartHomeControllerAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'first_registered', 'model')

admin.site.register(SmartHomeController, SmartHomeControllerAdmin)
admin.site.register(ControllerTask)
admin.site.register(ControllerCapability)
admin.site.register(ControllerPing)
admin.site.register(ControllerModel)

