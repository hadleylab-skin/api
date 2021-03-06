# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-14 06:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_participant'),
        ('moles', '0007_auto_20180312_0430'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudyInvitation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=255, verbose_name='Email address')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'New'), (2, 'Accepted'), (3, 'Declined')], default=1, verbose_name='Status')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Doctor', verbose_name='Doctor')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moles.Study', verbose_name='Study')),
            ],
            options={
                'verbose_name': 'Study invitation',
                'verbose_name_plural': 'Study invitations',
            },
        ),
    ]
