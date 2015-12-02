# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smarthome_admin', '0006_auto_20151123_1635'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='controllerping',
            name='controller',
        ),
        migrations.AddField(
            model_name='smarthomecontroller',
            name='ip',
            field=models.GenericIPAddressField(default='127.0.0.1'),
        ),
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(choices=[['Sockets', 'Sockets'], ['RemoteControl', 'RemoteControl'], ['Temperature', 'Temperature']], max_length=1024),
        ),
        migrations.DeleteModel(
            name='ControllerPing',
        ),
    ]
