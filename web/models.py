from datetime import datetime, timedelta
from uuid import uuid4

import misaka

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


LANGUAGES = (
    ('en', _('English')),
    ('cs', _('Czech')),
)


OCCASION_TYPES = (
    ('b', _('birthday')),
    ('n', _('nameday')),
)


def users_for_user(user):
    groups = user.groups.all()
    return User.objects.filter(
        groups__in=groups).exclude(pk=user.pk).distinct()


def get_users_to_nag():
    for user in User.objects.all():
        item_count = user.item_set.filter(already_given=False).count()

        if item_count == 0:
            yield user


def get_uuid():
    return str(uuid4()).replace('-', '')


class UserProfile(models.Model):
    language = models.CharField(max_length=2, choices=LANGUAGES, default='en')
    user = models.OneToOneField(User)
    subscribed_to_email = models.BooleanField(default=True)
    uuid = models.CharField(max_length=32, default=get_uuid)

    def __unicode__(self):
        return 'Profile for {}'.format(self.user.username)

    def get_unsubsribe_link(self):
        return reverse('unsubscribe', args=(self.uuid,))


class OccasionManager(models.Manager):

    def in_2_weeks(self, date=None):
        if not date:
            date = datetime.utcnow()

        two_weeks = date + timedelta(days=14)

        month = two_weeks.month
        day = two_weeks.day

        return self.filter(month=month, day=day)


class Occasion(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=1, choices=OCCASION_TYPES)

    month = models.IntegerField()
    day = models.IntegerField()

    objects = OccasionManager()


class Item(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255, verbose_name=_('Item name'))
    description = models.TextField(blank=True,
                                   verbose_name=_('Item description'))

    price = models.DecimalField(null=True, blank=True, max_digits=11,
                                decimal_places=2, default=None,
                                verbose_name=_('Estimated price'))

    already_given = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    multi_item = models.BooleanField(default=False)
    surprise = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    @property
    def buying(self):
        try:
            return self.buy_set.all()
        except IndexError:
            return None

    @property
    def html(self):
        return misaka.html(self.description, extensions=misaka.EXT_AUTOLINK)

    @property
    def type(self):
        return 'surprise' if self.surprise else 'item'


class Buy(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    purchased = models.BooleanField(default=False)

    amount = models.DecimalField(null=True, max_digits=11, decimal_places=2,
                                 default=None,
                                 verbose_name=_('My contribution'))

    def __unicode__(self):
        return '%s buying %s' % (self.user.username, self.item.name)

    @property
    def type(self):
        return 'buy'
