# Generated by Django 3.1.5 on 2021-03-30 22:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0017_auto_20210330_1805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='royale.taskschedule'),
        ),
    ]
