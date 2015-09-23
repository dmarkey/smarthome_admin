from rest_framework import serializers
from smarthome_admin.models import SmartHomeController, ControllerPing, ControllerModel, Socket

__author__ = 'dmarkey'


class SocketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Socket
        fields = ("id", 'state', 'human_name')


class ControllerSerializer(serializers.ModelSerializer):
    model = serializers.StringRelatedField()

    class Meta:
        model = SmartHomeController
        fields = ("id", 'model', 'human_name', "admin")


class ControllerPingSerializer(serializers.Serializer):

    controller_id = serializers.CharField(max_length=1024)
    model = serializers.CharField(max_length=1024)
    ip = serializers.CharField(max_length=1024)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        model = ControllerModel.objects.get(name=validated_data.get("model"))
        controller, _ = SmartHomeController.objects.get_or_create(unique_id=validated_data.get("controller_id"),
                                                                  model=model)
        cp = ControllerPing()
        cp.controller = controller
        cp.ip = validated_data['ip']
        cp.save()

        return validated_data