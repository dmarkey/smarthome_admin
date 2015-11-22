# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ControllerCapability',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('control_class', models.CharField(max_length=1024, choices=[['Temperature', 'Temperature'], ['Sockets', 'Sockets'], ['RemoteControl', 'RemoteControl']])),
                ('init_arguments', models.CharField(max_length=4096)),
                ('description', models.TextField()),
                ('route_name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='ControllerModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('capabilities', models.ManyToManyField(to='smarthome_admin.ControllerCapability')),
            ],
        ),
        migrations.CreateModel(
            name='ControllerPing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now=True)),
                ('ip', models.GenericIPAddressField()),
            ],
        ),
        migrations.CreateModel(
            name='ControllerTask',
            fields=[
                ('task_id', models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4)),
                ('description', models.CharField(max_length=4096)),
                ('name', models.CharField(max_length=1024)),
                ('arguments', models.CharField(max_length=1024)),
                ('creation_time', models.DateTimeField(auto_now=True)),
                ('status', models.SmallIntegerField(default=0, choices=[(0, 'CREATED'), (1, 'SENT'), (2, 'ACKNOWLEDGED'), (3, 'COMPLETE')])),
            ],
        ),
        migrations.CreateModel(
            name='RemoteEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('encoding', models.CharField(max_length=256)),
                ('value', models.IntegerField()),
                ('time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='SmartHomeController',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=1024)),
                ('unique_id', models.CharField(max_length=1024)),
                ('first_registered', models.DateTimeField(auto_now=True)),
                ('human_name', models.TextField(default='No name')),
                ('admin', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
                ('model', models.ForeignKey(to='smarthome_admin.ControllerModel')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, related_name='controller_users')),
            ],
        ),
        migrations.CreateModel(
            name='Socket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.SmallIntegerField()),
                ('state', models.BooleanField(default=False)),
                ('human_name', models.TextField()),
                ('admin', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, blank=True)),
                ('controller', models.ForeignKey(to='smarthome_admin.SmartHomeController')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, related_name='socket_users')),
            ],
        ),
        migrations.CreateModel(
            name='TemperatureRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('temperature', models.FloatField()),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('controller', models.ForeignKey(to='smarthome_admin.SmartHomeController')),
            ],
        ),
        migrations.AddField(
            model_name='remoteevent',
            name='controller',
            field=models.ForeignKey(to='smarthome_admin.SmartHomeController'),
        ),
        migrations.AddField(
            model_name='controllertask',
            name='controller',
            field=models.ForeignKey(to='smarthome_admin.SmartHomeController'),
        ),
        migrations.AddField(
            model_name='controllerping',
            name='controller',
            field=models.ForeignKey(to='smarthome_admin.SmartHomeController'),
        ),
    ]
