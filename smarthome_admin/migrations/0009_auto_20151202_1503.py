# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('smarthome_admin', '0008_auto_20151202_1210'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocketSet',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('sockets', models.ManyToManyField(to='smarthome_admin.Socket')),
            ],
        ),
        migrations.RemoveField(
            model_name='socketcontrol',
            name='socket',
        ),
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(max_length=1024, choices=[['Temperature', 'Temperature'], ['Sockets', 'Sockets'], ['RemoteControl', 'RemoteControl']]),
        ),
        migrations.AlterField(
            model_name='socketcontrol',
            name='action',
            field=models.SmallIntegerField(choices=[(0, 'Socket Off'), (1, 'Socket On'), (2, 'Socket Toggle')], default=0),
        ),
        migrations.AddField(
            model_name='socketcontrol',
            name='socket_set',
            field=models.ForeignKey(to='smarthome_admin.SocketSet', null=True),
        ),
    ]
