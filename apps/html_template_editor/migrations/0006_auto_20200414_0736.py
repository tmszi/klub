# Generated by Django 2.2.10 on 2020-04-14 05:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('html_template_editor', '0005_templatecontent_styles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companysocialmedia',
            name='icon_name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Icon name'),
        ),
    ]
