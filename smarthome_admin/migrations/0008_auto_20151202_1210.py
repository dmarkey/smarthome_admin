# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('smarthome_admin', '0007_auto_20151130_1417'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocketTimerSlot',
            fields=[
                ('socketcontrol_ptr', models.OneToOneField(to='smarthome_admin.SocketControl', serialize=False, parent_link=True, auto_created=True, primary_key=True)),
                ('enabled', models.BooleanField(default=False)),
                ('monday', models.BooleanField(default=False)),
                ('tuesday', models.BooleanField(default=False)),
                ('wednesday', models.BooleanField(default=False)),
                ('thursday', models.BooleanField(default=False)),
                ('friday', models.BooleanField(default=False)),
                ('saturday', models.BooleanField(default=False)),
                ('sunday', models.BooleanField(default=False)),
                ('start_time', models.TimeField()),
                ('stop_time', models.TimeField()),
            ],
            bases=('smarthome_admin.socketcontrol',),
        ),
        migrations.AddField(
            model_name='socketcontrol',
            name='creator',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(max_length=1024, choices=[['RemoteControl', 'RemoteControl'], ['Sockets', 'Sockets'], ['Temperature', 'Temperature']]),
        ),
    ]
