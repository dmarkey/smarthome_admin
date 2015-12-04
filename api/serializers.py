from rest_framework import serializers
from smarthome_admin.models import SmartHomeController, Socket

__author__ = 'dmarkey'


class SocketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Socket
        fields = ("id", 'state', 'human_name')


class ControllerSerializer(serializers.ModelSerializer):
    model = serializers.StringRelatedField()

    class Meta:
        model = SmartHomeController
        fields = ("id", 'model', 'human_name', "admin", "sockets", "capabilities", "extra_items")

