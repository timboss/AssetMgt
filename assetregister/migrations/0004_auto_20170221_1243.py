# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-02-21 12:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetregister', '0003_auto_20170221_1232'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calibrationrecord',
            name='calibration_fail',
        ),
        migrations.RemoveField(
            model_name='calibrationrecord',
            name='calibration_pass',
        ),
        migrations.AddField(
            model_name='calibrationrecord',
            name='calibration_outcome',
            field=models.CharField(choices=[('Pass', 'Pass'), ('Fail', 'Fail')], default='Pass', max_length=4),
        ),
    ]