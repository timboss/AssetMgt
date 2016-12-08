# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-11-22 11:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetregister', '0014_auto_20161014_1359'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='maintenance_instructions',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='calibration_instructions',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]