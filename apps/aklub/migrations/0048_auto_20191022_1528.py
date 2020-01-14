# Generated by Django 2.2.6 on 2019-10-22 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aklub', '0047_auto_20190919_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='donorpaymentchannel',
            name='SS',
            field=models.CharField(blank=True, help_text='Specific symbol', max_length=30, null=True, verbose_name='SS'),
        ),
        migrations.AlterField(
            model_name='accountstatements',
            name='type',
            field=models.CharField(choices=[('account', 'Account statement - Fio Banka'), ('account_cs', 'Account statement - Česká spořitelna'), ('account_kb', 'Account statement - Komerční Banka'), ('account_csob', 'Account statement - ČSOB'), ('account_sberbank', 'Account statement - Sberbank'), ('darujme', 'Darujme.cz')], max_length=20),
        ),
    ]