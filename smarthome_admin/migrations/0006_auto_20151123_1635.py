# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smarthome_admin', '0005_auto_20151122_2113'),
    ]

    operations = [
        migrations.AddField(
            model_name='socket',
            name='queued_task',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(max_length=1024, choices=[['Temperature', 'Temperature'], ['RemoteControl', 'RemoteControl'], ['Sockets', 'Sockets']]),
        ),
    ]
