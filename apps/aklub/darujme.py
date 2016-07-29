# -*- coding: utf-8 -*-
""" Parse reports from Darujme.cz """

from aklub.models import Payment, UserInCampaign, str_to_datetime, str_to_datetime_xml, UserProfile, Campaign, AccountStatements
from aklub.views import generate_variable_symbol
from django.contrib.auth.models import User
from django.core.exceptions import MultipleObjectsReturned
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _
from xml.dom import minidom
import datetime
import logging
import xlrd

# Text constants in Darujme.cz report
OK_STATES = ('OK, převedeno', 'OK')

MONTHLY = 'měsíční'
ONETIME = "jednorázový"
UNLIMITED = "na dobu neurčitou"

log = logging.getLogger(__name__)


def parse_string(value):
    if type(value) == float:
        return int(value)
    return value


def parse_float_to_int(value):
    return int(float(value))


def parse_darujme_xml(xmlfile):
    xmldoc = minidom.parse(xmlfile)
    darujme_api = xmldoc.getElementsByTagName('darujme_api')[0]
    payments = []
    skipped_payments = []
    for record in darujme_api.getElementsByTagName('record'):
        data = {}
        trans_id = record.getElementsByTagName('transaction_id')[0].firstChild
        if trans_id:
            data['id'] = trans_id.nodeValue
        else:
            data['id'] = ""
        data['projekt'] = record.getElementsByTagName('projekt')[0].firstChild.nodeValue
        data['cetnost'] = record.getElementsByTagName('cetnost')[0].firstChild.nodeValue
        cetnost_konec = record.getElementsByTagName('cetnost_konec')[0].firstChild
        if cetnost_konec:
            data['cetnost_konec'] = str_to_datetime_xml(cetnost_konec.nodeValue)
        else:
            data['cetnost_konec'] = UNLIMITED
        for hodnota in record.getElementsByTagName('uzivatelska_pole')[0].getElementsByTagName('hodnota'):
            if hodnota.hasChildNodes():
                value = hodnota.firstChild.nodeValue
            else:
                value = ""
            if value == "Ano":
                value = True
            if value == "Ne":
                value = False
            data[hodnota.attributes['nazev'].value] = value

        platby = record.getElementsByTagName('platby')
        if len(platby) > 0:
            for platba in platby[0].getElementsByTagName('platba'):
                data['datum_prichozi_platby'] = record.getElementsByTagName('datum_prichozi_platby')[0].firstChild.nodeValue
                data['obdrzena_castka'] = parse_float_to_int(platba.getElementsByTagName('obdrzena_castka')[0].firstChild.nodeValue)
                create_payment(data, payments, skipped_payments)
    return payments, skipped_payments


def create_statement_from_API(xmlfile):
    payments, skipped_payments = parse_darujme_xml(xmlfile)
    if len(payments) > 0:
        a = AccountStatements(type="darujme")
        a.payments = payments
        a.save()
    else:
        a = None
    return a, skipped_payments


def create_payment(data, payments, skipped_payments):
    if Payment.objects.filter(type='darujme', SS=data['id'], date=data['datum_prichozi_platby']).exists():
        skipped_payments.append({'ss': data['id'], 'date': data['datum_prichozi_platby'], 'name': data['jmeno'], 'surname': data['prijmeni'], 'email': data['email']})
        log.info('Payment with type Darujme.cz and SS=%s already exists, skipping' % str(data['id']))
        return None

    p = Payment()
    p.type = 'darujme'
    p.SS = data['id']
    p.date = data['datum_prichozi_platby']
    p.amount = data['obdrzena_castka']
    p.account_name = u'%s, %s' % (data['prijmeni'], data['jmeno'])
    p.user_identification = data['email']

    if data['cetnost_konec'] != UNLIMITED:
        cetnost_konec = data['cetnost_konec']
    else:
        cetnost_konec = None

    if data['cetnost'] == MONTHLY:
        cetnost = "monthly"
    else:
        cetnost = None

    try:
        campaign = Campaign.objects.get(darujme_name=data['projekt'])
        user, user_created = User.objects.get_or_create(
            email=data['email'],
            defaults={
                'first_name': data['jmeno'],
                'last_name': data['prijmeni'],
                'username': '%s%s' % (data['email'].split('@', 1)[0], User.objects.count()),
            })
        userprofile, userprofile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'street': data['ulice'],
                'city': data['mesto'],
                'zip_code': data['psc'],
            })
        userincampaign, userincampaign_created = UserInCampaign.objects.get_or_create(
            userprofile=userprofile,
            campaign=campaign,
            defaults={
                'variable_symbol': generate_variable_symbol(),
                'wished_tax_confirmation': data['potvrzeni_daru'],
                'regular_frequency': cetnost,
                'regular_payments': cetnost is not None,
                'regular_amount': data['obdrzena_castka'] if cetnost else None,
                'end_of_regular_payments': cetnost_konec,
            })
        p.user = userincampaign

        if userincampaign_created:
            log.info('UserInCampaign with email %s created' % data['email'])
    except MultipleObjectsReturned:
        log.info('Duplicate email %s' % data['email'])
        raise ValidationError(_('Duplicate email %(email)s'), params={'email': data['email']})
    payments.append(p)


def parse_darujme(xlsfile):
    log.info('Darujme.cz import started at %s' % datetime.datetime.now())
    book = xlrd.open_workbook(file_contents=xlsfile.read())
    sheet = book.sheet_by_index(0)
    payments = []
    skipped_payments = []
    for ir in range(1, sheet.nrows):
        data = {}

        row = sheet.row(ir)
        log.debug('Parsing transaction: %s' % row)

        # Darujme.cz ID of the transaction
        if row[0].value:
            data['id'] = int(row[0].value)
        else:
            data['id'] = ""

        # Skip all non klub transactions (e.g. PNK)
        data['projekt'] = row[2].value

        # Amount sent by the donor in CZK
        # The money we receive is smaller by Darujme.cz
        # margin, but we must count the whole ammount
        # to issue correct tax confirmation to the donor
        state = row[9].value
        if state not in OK_STATES:
            continue

        data['obdrzena_castka'] = int(row[5].value)

        data['datum_prichozi_platby'] = str_to_datetime(row[12].value)
        data['jmeno'] = row[17].value
        data['prijmeni'] = row[18].value
        data['email'] = row[19].value
        data['ulice'] = row[20].value
        data['mesto'] = row[21].value
        data['psc'] = parse_string(row[22].value)
        data['potvrzeni_daru'] = row[23].value
        data['cetnost'] = row[13].value
        cetnost_konec = row[14].value
        if cetnost_konec != UNLIMITED:
            data['cetnost_konec'] = str_to_datetime(cetnost_konec)
        else:
            data['cetnost_konec'] = cetnost_konec

        create_payment(data, payments, skipped_payments)
    return payments, skipped_payments
