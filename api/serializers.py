from rest_framework import serializers
from smarthome_controller.models import SmartHomeController, ControllerPing, ControllerModel

__author__ = 'dmarkey'


class ControllerPingSerializer(serializers.Serializer):

    controller_id = serializers.CharField(max_length=1024)
    model = serializers.CharField(max_length=1024)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        model = ControllerModel.objects.get(name=validated_data.get("model"))
        controller, _ = SmartHomeController.objects.get_or_create(unique_id=validated_data.get("controller_id"),
                                                                  model=model)
        cp = ControllerPing()
        cp.controller = controller
        cp.save()

        return validated_data