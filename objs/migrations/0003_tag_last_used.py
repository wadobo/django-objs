# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('objs', '0002_projectdedication_commentary'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='last_used',
            field=models.DateTimeField(default=datetime.datetime(2015, 12, 21, 10, 3, 35, 526946), auto_now_add=True),
            preserve_default=False,
        ),
    ]
