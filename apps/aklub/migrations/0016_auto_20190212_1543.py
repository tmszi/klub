# Generated by Django 2.1.7 on 2019-02-12 14:43

import aklub.autocom
import aklub.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smmapdfs', '0002_auto_20180611_1830'),
        ('aklub', '0015_auto_20190206_1104'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaxConfirmationField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(default=None, max_length=36, verbose_name='field')),
                ('font_size', models.IntegerField(default=16, verbose_name='Font size')),
                ('x', models.FloatField(default=0, verbose_name='X (mm)')),
                ('y', models.FloatField(default=0, verbose_name='Y (mm)')),
                ('alignment', models.CharField(choices=[('left', 'Left'), ('right', 'Right'), ('center', 'Center')], default='left', max_length=36, verbose_name='alignment')),
                ('font', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='smmapdfs.PdfSandwichFont')),
                ('pdfsandwich_type', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='smmapdfs.PdfSandwichType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaxConfirmationPdf',
            fields=[
                ('pdfsandwichabc_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='smmapdfs.PdfSandwichABC')),
            ],
            bases=('smmapdfs.pdfsandwichabc',),
        ),
        migrations.AlterField(
            model_name='masscommunication',
            name='template',
            field=models.TextField(help_text='Template can contain following variable substitutions: <br/>{mr|mrs} or {mr/mrs}, $addressment, $name, $firstname, $surname, $street, $city, $zipcode, $email, $telephone, $regular_amount, $regular_frequency, $var_symbol, $last_payment_amount, $auth_token', max_length=50000, null=True, validators=[aklub.autocom.gendrify_text, django.core.validators.RegexValidator('^([^$]*(\\$(addressment|name|firstname|surname|street|city|zipcode|email|telephone|regular_amount|regular_frequency|var_symbol|last_payment_amount|auth_token)\\b)?)*$', 'Unknown variable')], verbose_name='Template'),
        ),
        migrations.AlterField(
            model_name='taxconfirmation',
            name='file',
            field=models.FileField(storage=aklub.models.OverwriteStorage(), upload_to=''),
        ),
        migrations.AddField(
            model_name='taxconfirmationpdf',
            name='obj',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='aklub.TaxConfirmation'),
        ),
    ]