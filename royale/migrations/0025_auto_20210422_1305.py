# Generated by Django 3.1.5 on 2021-04-22 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0024_auto_20210408_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventparticipation',
            name='attack_damage',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='eventparticipation',
            name='damage_taken',
            field=models.IntegerField(default=0),
        ),
    ]
