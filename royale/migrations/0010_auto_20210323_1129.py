# Generated by Django 3.1.5 on 2021-03-23 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0009_auto_20210323_1117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_key',
            field=models.CharField(max_length=10, null=True, unique=True),
        ),
    ]
