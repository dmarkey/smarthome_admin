# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smarthome_admin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(choices=[['Sockets', 'Sockets'], ['RemoteControl', 'RemoteControl'], ['Temperature', 'Temperature']], max_length=1024),
        ),
    ]
