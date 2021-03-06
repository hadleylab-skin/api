# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-08 07:00
from __future__ import unicode_literals

import apps.moles.models.upload_paths
from decimal import Decimal
import django.contrib.postgres.fields.jsonb
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import versatileimagefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnatomicalSite',
            fields=[
                ('slug', models.SlugField(editable=False, primary_key=True, serialize=False, verbose_name='Slug')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='moles.AnatomicalSite', verbose_name='Parent anatomical site')),
            ],
            options={
                'verbose_name': 'Anatomical site',
                'verbose_name_plural': 'Anatomical sites',
            },
        ),
        migrations.CreateModel(
            name='Mole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position_x', models.IntegerField(verbose_name='Position x')),
                ('position_y', models.IntegerField(verbose_name='Position y')),
                ('anatomical_site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moles.AnatomicalSite', verbose_name='Anatomical site')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='moles', to='accounts.Patient', verbose_name='Patient')),
            ],
            options={
                'verbose_name': 'Mole',
                'verbose_name_plural': 'Moles',
            },
        ),
        migrations.CreateModel(
            name='MoleImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('path_diagnosis', models.CharField(blank=True, max_length=100, verbose_name='Path diagnosis')),
                ('clinical_diagnosis', models.CharField(blank=True, max_length=100, verbose_name='Clinical diagnosis')),
                ('prediction', models.CharField(blank=True, default='Unknown', max_length=100, verbose_name='Prediction')),
                ('prediction_accuracy', models.DecimalField(blank=True, decimal_places=3, default=Decimal('0'), max_digits=5, null=True, verbose_name='Prediction accuracy')),
                ('photo', versatileimagefield.fields.VersatileImageField(blank=True, max_length=300, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=apps.moles.models.upload_paths.mole_image_photo_path, verbose_name='Photo')),
                ('biopsy', models.BooleanField(default=False, verbose_name='Biopsy')),
                ('biopsy_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='Biopsy data')),
                ('mole', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='moles.Mole', verbose_name='Mole')),
            ],
            options={
                'verbose_name': 'Mole image',
                'verbose_name_plural': 'Mole images',
                'ordering': ('-date_created',),
            },
        ),
        migrations.CreateModel(
            name='PatientAnatomicalSite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('distant_photo', versatileimagefield.fields.VersatileImageField(blank=True, max_length=300, null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=apps.moles.models.upload_paths.distant_photo_path, verbose_name='Distant photo')),
                ('anatomical_site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='moles.AnatomicalSite', verbose_name='Anatomical site')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='anatomical_sites', to='accounts.Patient', verbose_name='Patient')),
            ],
            options={
                'verbose_name': 'Patient anatomical site',
                'verbose_name_plural': 'Patient anatomical sites',
            },
        ),
    ]
