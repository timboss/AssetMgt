# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2016-04-13 12:55
from __future__ import unicode_literals

import assetregister.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assetregister', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='asset_image',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=assetregister.models.img_path_and_rename),
        ),
    ]
