from rest_framework import serializers
from smarthome_controller.models import SmartHomeController, ControllerPing, TYPES

__author__ = 'dmarkey'


class ControllerPingSerializer(serializers.Serializer):


    controller_id = serializers.CharField(max_length=1024)
    type = serializers.ChoiceField(choices=TYPES)


    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        controller, _ = SmartHomeController.objects.get_or_create(unique_id=validated_data.get("controller_id"),
                                                                  type=validated_data.get("type"))
        cp = ControllerPing()
        cp.controller = controller
        cp.save()

        return validated_data