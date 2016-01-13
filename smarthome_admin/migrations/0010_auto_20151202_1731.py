# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('smarthome_admin', '0009_auto_20151202_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='socket',
            name='attached_device',
            field=django_resized.forms.ResizedImageField(null=True, upload_to='', blank=True),
        ),
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(choices=[['RemoteControl', 'RemoteControl'], ['Temperature', 'Temperature'], ['Sockets', 'Sockets']], max_length=1024),
        ),
    ]
