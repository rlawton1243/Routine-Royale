# Generated by Django 3.1.5 on 2021-03-30 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0018_auto_20210330_1806'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taskstep',
            name='completed',
        ),
        migrations.AddField(
            model_name='eventparticipation',
            name='completed_steps',
            field=models.ManyToManyField(to='royale.TaskStep'),
        ),
    ]
