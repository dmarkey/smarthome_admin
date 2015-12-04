from django.contrib import admin
from .models import SmartHomeController, ControllerTask, RemoteEvent, ControllerCapability, \
    ControllerModel, Socket, TemperatureRecord, RegisteredRemoteEvent, SocketTimerSlot, SocketSet

__author__ = 'dmarkey'

class SmartHomeControllerAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'first_registered', 'model', 'name')


class PingAdmin(admin.ModelAdmin):
    list_display = ('controller', 'time')


def toggle(modeladmin, request, queryset):
    for socket in queryset:
        modeladmin.message_user(request, str(socket.toggle()))

toggle.short_description = "Toggle these sockets."


class SocketAdmin(admin.ModelAdmin):
    list_display = ['number', 'controller', 'state']
    actions = [toggle]


class TaskAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'controller', 'status']


class TemperatureAdmin(admin.ModelAdmin):
    list_display = ['controller', 'temperature', "time"]


class SocketControlAdmin(admin.ModelAdmin):
    exclude = ["creator"]

    def save_model(self, request, obj, form, change):
        obj.creator = request.user
        obj.save()


class RemoteEventAdmin(admin.ModelAdmin):
    list_display = ['controller', 'encoding', "value"]


class RegisteredRemoteEventAdmin(SocketControlAdmin):
    list_display = ['socket_set', 'encoding', "value"]


class SocketTimerSlotAdmin(admin.ModelAdmin):
    exclude = ["creator", "timer"]
    list_display = ["socket_set", 'timer', "get_schedule"]


admin.site.register(SmartHomeController, SmartHomeControllerAdmin)
admin.site.register(ControllerTask, TaskAdmin)
admin.site.register(ControllerCapability)
admin.site.register(ControllerModel)
admin.site.register(TemperatureRecord, TemperatureAdmin)
admin.site.register(Socket, SocketAdmin)
admin.site.register(RemoteEvent, RemoteEventAdmin)
admin.site.register(SocketTimerSlot, SocketTimerSlotAdmin)
admin.site.register(RegisteredRemoteEvent, RegisteredRemoteEventAdmin)
admin.site.register(SocketSet)
