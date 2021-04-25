# Generated by Django 3.1.5 on 2021-04-22 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0028_useractiontypes_energy_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraction',
            name='performer',
        ),
        migrations.AddField(
            model_name='useraction',
            name='performer',
            field=models.ManyToManyField(related_name='performer', to='royale.Client'),
        ),
        migrations.RemoveField(
            model_name='useraction',
            name='target',
        ),
        migrations.AddField(
            model_name='useraction',
            name='target',
            field=models.ManyToManyField(to='royale.Client'),
        ),
    ]