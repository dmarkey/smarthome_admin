__author__ = 'dmarkey'
from django.contrib import admin
from models import SmartHomeController, ControllerPing, ControllerTask, ControllerCapability, ControllerModel, Socket


class SmartHomeControllerAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'first_registered', 'model')


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


admin.site.register(SmartHomeController, SmartHomeControllerAdmin)
admin.site.register(ControllerTask, TaskAdmin)
admin.site.register(ControllerCapability)
admin.site.register(ControllerPing, PingAdmin)
admin.site.register(ControllerModel)
admin.site.register(Socket, SocketAdmin)

