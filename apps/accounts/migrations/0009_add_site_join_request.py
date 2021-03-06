# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-17 13:04
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django_fsm
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [('accounts', '0008_doctor_approved_by_coordinator'), ]

    operations = [
        migrations.CreateModel(
            name='SiteJoinRequest',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID')),
                ('state', django_fsm.FSMIntegerField(default=0)),
                ('date_created', models.DateTimeField(
                    auto_now_add=True,
                    default=datetime.datetime(
                        2017, 10, 19, 13, 18, 35, 239551, tzinfo=utc))),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ]),
        migrations.RemoveField(
            model_name='doctor',
            name='approved_by_coordinator', ),
        migrations.AddField(
            model_name='sitejoinrequest',
            name='doctor',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='accounts.Doctor'), ),
        migrations.AddField(
            model_name='sitejoinrequest',
            name='site',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='accounts.Site'), ),
        migrations.AlterUniqueTogether(
            name='sitejoinrequest',
            unique_together=set([('doctor', 'site')]), ),
    ]
