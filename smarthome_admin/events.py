import traceback

from smarthome_admin.models import ControllerModel

__author__ = 'dmarkey'
import json

#import paho.mqtt.client as mqtt
from django.conf import settings


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
    client.subscribe("/admin/#")


def task_status(obj):
    from .models import ControllerTask
    try:
        task = ControllerTask.objects.get(task_id=obj['task_id'])
        task.status = obj['status']
        task.save()

        if task.status == 3:
            task.controller.queue_next_task()

    except:
        print("Error")


def incoming_event(obj):
    from .models import SmartHomeController
    controller_id = obj['controller_id']
    try:
        controller = SmartHomeController.objects.get(unique_id=controller_id)
    except SmartHomeController.DoesNotExist:
        model = ControllerModel.objects.get(name=obj['model'])
        controller, _ = SmartHomeController.objects.get_or_create(unique_id=controller_id,
                                                                  model=model)
    if obj['event'] == "task_status":
        task_status(obj)
        return

    if obj['route'] == "All":
        if obj['event'] == "BEACON":
            controller.clear_tasks()
            print(obj)

        caps = controller.model.capabilities.all()
    else:
        caps = controller.model.capabilities.filter(route_name=obj['route'])
    for cap in caps:
        cap.event(controller, obj)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        if msg.topic == "/admin/task_status":
            task_status(msg)
        if msg.topic == "/admin/events":
            incoming_event(msg)
    except:
        traceback.print_exc()

    print(msg.topic+" "+str(msg.payload))


def on_publish(client, userdata, mid):
    print(mid)

#client = mqtt.Client()


def start_sub():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings.MQTT_SERVER, settings.MQTT_PORT, 60)
    client.loop_forever()


def start_pub():
    client.connect(settings.MQTT_SERVER, settings.MQTT_PORT, 60)
    client.loop_start()
