# -*- coding: utf-8 -*-
# Author: Petr Dlouhý <petr.dlouhy@email.cz>
#
# Copyright (C) 2013 o.s. Auto*Mat
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
import copy
import datetime

from django.contrib import messages
from django.utils.translation import ugettext as _

from . import autocom
from .models import AutomaticCommunication, Communication, MassCommunication, Payment, TaxConfirmationPdf, UserInCampaign, UserProfile
"""Mailing"""


def create_fake_userincampaign(sending_user):
    # create fake values
    userprofile = sending_user
    userincampaign = UserInCampaign(
        userprofile=userprofile,
        regular_amount=123456,
        regular_frequency="monthly",
        variable_symbol=12345678,
        last_payment=Payment(amount=12345),
    )
    return userincampaign


def get_template_subject_for_language(obj, language):
    if language == 'cs':
        return obj.template, obj.subject
    else:
        return obj.template_en, obj.subject_en


def send_fake_communication(communication, sending_user, request):
    from .tasks import send_communication_task
    if isinstance(communication, AutomaticCommunication):
        communication_type = 'automatic'
    else:
        communication_type = 'mass'
    send_communication_task.apply_async(args=(communication.id, communication_type, "fake_user", sending_user.id))
    messages.add_message(request, messages.INFO, _("Testing communication sending was queued"))


def send_mass_communication(communication, sending_user, request):
    from .tasks import create_mass_communication_tasks
    create_mass_communication_tasks.apply_async(args=(communication.id, sending_user.id))
    messages.add_message(request, messages.INFO, _("Communication sending was queued for %s users") % communication.send_to_users.count())


def create_mass_communication_tasks_sync(communication_id, sending_user_id):
    from .tasks import send_communication_task
    communication = MassCommunication.objects.get(id=communication_id)
    for userincampaign in communication.send_to_users.all():
        send_communication_task.apply_async(args=(communication.id, 'mass', userincampaign.id, sending_user_id))


def send_communication_sync(communication_id, communication_type, userincampaign_id, sending_user_id):
    sending_user = UserProfile.objects.get(id=sending_user_id)
    if userincampaign_id == "fake_user":
        userincampaign = create_fake_userincampaign(sending_user)
        save = False
    else:
        userincampaign = UserInCampaign.objects.get(id=userincampaign_id)
        save = True
    if communication_type == 'mass':
        mass_communication = MassCommunication.objects.get(id=communication_id)
    else:
        mass_communication = AutomaticCommunication.objects.get(id=communication_id)

    template, subject = get_template_subject_for_language(mass_communication, userincampaign.userprofile.language)
    if userincampaign.userprofile.is_active and subject and subject.strip() != '':
        if not subject or subject.strip() == '' or not template or template.strip('') == '':
            raise Exception("Message template is empty for one of the language variants.")
        if hasattr(mass_communication, "attach_tax_confirmation") and not mass_communication.attach_tax_confirmation:
            attachment = copy.copy(mass_communication.attachment)
        else:
            tax_confirmations = TaxConfirmationPdf.objects.filter(
                obj__user_profile=userincampaign.userprofile,
                obj__year=datetime.datetime.now().year - 1,
            )
            if len(tax_confirmations) > 0:
                attachment = copy.copy(tax_confirmations[0].pdf)
            else:
                attachment = None
        c = Communication(
            user=userincampaign, method=mass_communication.method, date=datetime.datetime.now(),
            subject=autocom.process_template(subject, userincampaign),
            summary=autocom.process_template(template, userincampaign),
            attachment=attachment,
            note=_("Prepared by auto*mated mass communications at %s") % datetime.datetime.now(),
            send=True, created_by=sending_user, handled_by=sending_user,
            type='mass',
        )
        c.dispatch(save=save)
