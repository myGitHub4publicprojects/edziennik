# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2017-04-13 19:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClassDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('date_of_class', models.DateField()),
                ('subject', models.CharField(default=b'testowy temat', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Grades',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('date_of_test', models.DateField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
                ('score', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Lector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SMS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('service', models.CharField(choices=[(b'smsapipl', b'smsapipl'), (b'twilio', b'twilio')], max_length=10)),
                ('message', models.TextField(max_length=1600)),
                ('delivered', models.BooleanField()),
                ('twilio_message_sid', models.CharField(blank=True, max_length=120, null=True)),
                ('twilio_message_status', models.CharField(blank=True, max_length=120, null=True)),
                ('smsapipl_message_id', models.CharField(blank=True, max_length=120, null=True)),
                ('smsapipl_status', models.CharField(blank=True, max_length=120, null=True)),
                ('smsapipl_error_code', models.CharField(blank=True, max_length=120, null=True)),
                ('smsapipl_error_message', models.CharField(blank=True, max_length=120, null=True)),
                ('addressee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('gender', models.CharField(choices=[(b'M', b'Male'), (b'F', b'Female')], max_length=1)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edziennik.Group')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edziennik.Parent')),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='lector',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edziennik.Lector'),
        ),
        migrations.AddField(
            model_name='grades',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='edziennik.Student'),
        ),
        migrations.AddField(
            model_name='classdate',
            name='student',
            field=models.ManyToManyField(to='edziennik.Student'),
        ),
    ]
