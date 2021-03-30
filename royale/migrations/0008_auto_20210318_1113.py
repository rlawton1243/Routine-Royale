# Generated by Django 3.1.5 on 2021-03-18 15:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0007_auto_20210317_1535'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='task_list',
        ),
        migrations.AddField(
            model_name='task',
            name='associated_event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='royale.event'),
            preserve_default=False,
        ),
    ]