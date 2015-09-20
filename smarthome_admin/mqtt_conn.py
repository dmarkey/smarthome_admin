__author__ = 'dmarkey'
import json

import paho.mqtt.client as mqtt

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
    client.subscribe("/admin/#")


def task_status(msg):
    obj = json.loads(msg.payload.decode("utf-8"))
    from .models import ControllerTask
    ControllerTask.objects.filter(task_id=obj['task_id']).update(status=obj['status'])


def incoming_beacon(msg):
    from .models import SmartHomeController
    obj = json.loads(msg.payload.decode("utf-8"))
    controller_id = obj['controller_id']
    controller = SmartHomeController.objects.get(unique_id=controller_id)
    for cap in controller.model.capabilities.all():
        cap.incoming_beacon(controller)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    if msg.topic == "/admin/task_status":
        task_status(msg)
    if msg.topic == "/admin/beacon":
        incoming_beacon(msg)
    print(msg.topic+" "+str(msg.payload))


def on_publish(client, userdata, mid):
    print(mid)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("dmarkey.mooo.com", 8000, 60)

client.loop_start()