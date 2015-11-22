# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smarthome_admin', '0004_auto_20151122_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='socketcontrol',
            name='timer',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(max_length=1024, choices=[['Temperature', 'Temperature'], ['Sockets', 'Sockets'], ['RemoteControl', 'RemoteControl']]),
        ),
    ]
