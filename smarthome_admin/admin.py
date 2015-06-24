__author__ = 'dmarkey'
from django.contrib import admin
from models import SmartHomeController, ControllerPing, ControllerTask, ControllerCapability, ControllerModel, Socket


class SmartHomeControllerAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'first_registered', 'model')


class PingAdmin(admin.ModelAdmin):
    list_display = ('controller', 'time')


def toggle(modeladmin, request, queryset):
    [socket.toggle() for socket in queryset]

toggle.short_description = "Toggle these sockets."


class SocketAdmin(admin.ModelAdmin):
    list_display = ['number', 'controller']
    actions = [toggle]

admin.site.register(SmartHomeController, SmartHomeControllerAdmin)
admin.site.register(ControllerTask)
admin.site.register(ControllerCapability)
admin.site.register(ControllerPing, PingAdmin)
admin.site.register(ControllerModel)
admin.site.register(Socket, SocketAdmin)

