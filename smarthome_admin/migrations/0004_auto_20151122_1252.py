# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smarthome_admin', '0003_auto_20151122_1233'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocketControl',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('action', models.SmallIntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='controllercapability',
            name='control_class',
            field=models.CharField(max_length=1024, choices=[['RemoteControl', 'RemoteControl'], ['Sockets', 'Sockets'], ['Temperature', 'Temperature']]),
        ),
        migrations.CreateModel(
            name='RegisteredRemoteEvent',
            fields=[
                ('socketcontrol_ptr', models.OneToOneField(to='smarthome_admin.SocketControl', serialize=False, primary_key=True, auto_created=True, parent_link=True)),
                ('encoding', models.CharField(max_length=256)),
                ('value', models.IntegerField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
            bases=('smarthome_admin.socketcontrol',),
        ),
        migrations.AddField(
            model_name='socketcontrol',
            name='socket',
            field=models.ForeignKey(to='smarthome_admin.Socket'),
        ),
    ]
