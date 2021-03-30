# Generated by Django 3.1.5 on 2021-03-23 21:23

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0012_auto_20210323_1132'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='event_key',
        ),
        migrations.AddField(
            model_name='event',
            name='event_complete_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]
