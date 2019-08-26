# Generated by Django 2.2.4 on 2019-08-19 14:16

from django.db import migrations
from aklub.models import UserProfile, Preference, AdministrativeUnit

class Migration(migrations.Migration):

    def preference_tables_create(apps, schema_editor):
        for user in UserProfile.objects.all():
            for unit in user.administrative_units.all():
                Preference.objects.get_or_create(
                    user=user,
                    administrative_unit=unit,
                )




    dependencies = [
        ('aklub', '0034_auto_20190819_1530'),
    ]

    operations = [
        migrations.RunPython(preference_tables_create),
    ]