# custom filters

from django.utils.translation import ugettext as _
from django.contrib.admin import SimpleListFilter
from django.db.models import Sum, Count, Q
from datetime import date

from models import Condition, User
import models
import autocom

class NullFieldFilter(SimpleListFilter):
    """This fiters nullable fields by 
           'All' (no filter),
           'Empty' (field__isnull=True filter)
           'Filled in' (not null).

       Child classes must override the field attribute
       to specify which field this filter should be applied to."""

    field=None

    def lookups(self, request, model_admin):
        return (('filled', _('Filled-in')),
                ('empty', _('Empty')))

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        return queryset.filter(**{'%s__isnull' % self.field: self.value()=='empty' and True})

class PaymentsAssignmentsFilter(NullFieldFilter):
    field = 'user'
    title = _("User assignment")
    parameter_name = 'user_assignment'

class UserConditionFilter(SimpleListFilter):
    """Filters using computed dynamic conditions from DB"""

    title = _("Condition")
    parameter_name = 'user_condition'

    def lookups(self, request, model_admin):
        return [(cond.id, cond.name) for cond in Condition.objects.filter(as_filter=True)]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        cond = Condition.objects.filter(id=self.value())[0]

        return models.filter_by_condition(queryset, cond)


class UserConditionFilter1(UserConditionFilter):
    """Filters using computed dynamic conditions from DB"""
    parameter_name = 'user_condition1'


class ActiveCampaignFilter(SimpleListFilter):
    title = u"Active"
    parameter_name = u'active'

    def lookups(self, request, model_admin):
        return (
            ('yes', _(u'Yes')),
            ('no', _(u'No')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(Q(terminated__gte = date.today()) | Q(terminated = None), created__lte = date.today())
        if self.value() == 'no':
            return queryset.exclude(Q(terminated__gte = date.today()) | Q(terminated = None), created__lte = date.today())

