# Generated by Django 3.1.5 on 2021-03-17 19:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0004_auto_20210317_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskschedule',
            name='schedule_tasks',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='royale.task'),
        ),
    ]
