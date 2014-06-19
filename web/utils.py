from datetime import datetime, timedelta

from django.utils import translation
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string

from models import Buy, Item


DOMAIN = getattr(settings, 'DOMAIN')


def get_latest_for_user(user, delta=None):
    latest_items = Item.objects.exclude(
        user=user).order_by('-created')

    latest_buys = Buy.objects.exclude(user=user).exclude(
        item__user=user).order_by('-created')

    if delta:
        latest_items = latest_items.filter(created__gt=delta)
        latest_buys = latest_buys.filter(created__gt=delta)

    latest = list(latest_items) + list(latest_buys)
    latest.sort(key=lambda x: x.created)
    latest.reverse()

    return latest


def render_weekly_email_for_user(user):
    week_ago = datetime.utcnow() - timedelta(days=7)
    latest = get_latest_for_user(user, delta=week_ago)

    if not latest:
        return

    email = render_to_string('email.html', {
        'user': user,
        'latest': latest,
        'DOMAIN': DOMAIN
    })

    return email


def send_weekly_email_for_user(user):
    if not user.email:
        return

    original_language = translation.get_language()

    try:
        translation.activate(user.userprofile.language)

        email = render_weekly_email_for_user(user)

        if email:
            subject = _('This week on the wishlist')
            send_mail(subject, email, 'wishlist@wishlist.pokorny.ca',
                      [user.email], fail_silently=False)

    finally:
        translation.activate(original_language)
