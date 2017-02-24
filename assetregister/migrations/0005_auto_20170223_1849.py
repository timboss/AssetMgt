# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-02-23 18:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetregister', '0004_auto_20170221_1243'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='ok_to_use',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='calibrationrecord',
            name='calibration_outcome',
            field=models.CharField(choices=[('Pass', 'Pass'), ('Fail', 'Fail')], default='Pass', max_length=10),
        ),
    ]
