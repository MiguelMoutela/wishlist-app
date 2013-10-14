import misaka
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class Item(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255, verbose_name=_('Item name'))
    description = models.TextField(blank=True,
                                   verbose_name=_('Item description'))

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    @property
    def buying(self):
        try:
            return self.buy_set.all()[0]
        except IndexError:
            return None

    @property
    def html(self):
        return misaka.html(self.description, extensions=misaka.EXT_AUTOLINK)

    @property
    def type(self):
        return 'item'


class Buy(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item)

    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return '%s buying %s' % (self.user.username, self.item.name)

    @property
    def type(self):
        return 'buy'


class Action(models.Model):
    TYPES = (
        ('1', _('added an item'),),
        ('2', _('committed to buy an item'),),
    )
    user = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(Item)
    type = models.CharField(max_length=1, choices=TYPES)

    def render(self):
        return u'{} {}'.format(self.user.first_name, self.get_type_display())
