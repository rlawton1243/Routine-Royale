# Generated by Django 3.1.5 on 2021-03-30 21:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('royale', '0015_auto_20210330_1650'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventparticipation',
            name='selected_class',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='royale.clazz'),
        ),
    ]