from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Starts the MQTT listener'

    def handle(self, *args, **options):
        from smarthome_admin.mqtt_conn import start_sub
        start_sub()
