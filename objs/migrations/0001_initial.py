# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Iteration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('end', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='ObjUser',
            fields=[
                ('user', models.ForeignKey(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
                ('worklog', models.TextField()),
                ('worklog_lastmodified', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectDedication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dedicated', models.FloatField()),
                ('time', models.DateTimeField()),
                ('it', models.ForeignKey(to='objs.Iteration', on_delete=models.CASCADE)),
                ('pr', models.ForeignKey(to='objs.Project', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='ProjectDedicationTagged',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_dedication', models.ForeignKey(to='objs.ProjectDedication', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='UserDedication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hours', models.FloatField()),
                ('it', models.ForeignKey(to='objs.Iteration', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='UserDedicationPr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('percentage', models.FloatField()),
                ('pr', models.ForeignKey(to='objs.Project', on_delete=models.CASCADE)),
                ('userd', models.ForeignKey(related_name='dedicationpr', to='objs.UserDedication', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='projectdedicationtagged',
            name='tag',
            field=models.ForeignKey(to='objs.Tag', on_delete=models.CASCADE),
        ),
    ]
