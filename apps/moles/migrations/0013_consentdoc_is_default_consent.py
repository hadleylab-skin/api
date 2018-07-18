# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-07-18 03:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('moles', '0012_auto_20180614_0419'),
    ]

    operations = [
        migrations.AddField(
            model_name='consentdoc',
            name='is_default_consent',
            field=models.BooleanField(default=False, verbose_name='Used as part of default consent form'),
        ),
    ]
