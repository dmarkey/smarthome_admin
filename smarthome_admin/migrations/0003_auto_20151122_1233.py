# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smarthome_admin', '0002_auto_20151122_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(max_length=1024, choices=[['RemoteControl', 'RemoteControl'], ['Temperature', 'Temperature'], ['Sockets', 'Sockets']]),
        ),
    ]
