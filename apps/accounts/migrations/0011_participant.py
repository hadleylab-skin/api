# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-14 06:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20171030_0837'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('doctor_ptr', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='participant_role', serialize=False, to='accounts.Doctor')),
            ],
            options={
                'verbose_name': 'Participant',
                'verbose_name_plural': 'Participants',
            },
        ),
    ]