# Generated by Django 2.2.8 on 2020-01-08 08:07

import aklub.autocom
import colorfield.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0059_auto_20200102_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='administrativeunit',
            name='color',
            field=colorfield.fields.ColorField(default='#000000', help_text='Choose color to help discern Administrative unit in app', max_length=18),
        ),
    ]