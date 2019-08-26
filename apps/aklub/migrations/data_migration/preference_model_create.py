# -*- coding: utf-8 -*-

def preference_model_create(apps, schema_editor):
    profile_model = apps.get_model('aklub', 'UserProfile')
    preference_model = apps.get_model('aklub', 'Preference')
    for user in profile_model.objects.all():
        for unit in user.administrative_units.all():
            preference_model.objects.get_or_create(
                user=user,
                administrative_unit=unit,
            )
