# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('objs', '0003_tag_last_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='last_used',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
