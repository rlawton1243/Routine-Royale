# Generated by Django 3.1.5 on 2021-03-17 19:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0005_auto_20210317_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='task_steps',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='royale.tasksteps'),
        ),
    ]
