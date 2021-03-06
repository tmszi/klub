# Generated by Django 2.1.5 on 2019-02-02 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Repo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Repo name')),
                ('account', models.CharField(max_length=256, verbose_name='Account')),
                ('provider', models.CharField(choices=[('github', 'github')], default='github', max_length=64, verbose_name='Repo host')),
            ],
        ),
    ]
