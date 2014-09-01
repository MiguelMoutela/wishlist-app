from datetime import datetime, timedelta
from contextlib import contextmanager

from django.utils import translation
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from models import Buy, Item


DOMAIN = getattr(settings, 'DOMAIN')
DUMMY_USERS = getattr(settings, 'DUMMY_USERS', [])


@contextmanager
def user_language(language):
    original_language = translation.get_language()

    try:
        translation.activate(language)
        yield
    finally:
        translation.activate(original_language)


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


def send_email_to_user(user, subject, message):
    original_language = translation.get_language()

    try:
        translation.activate(user.userprofile.language)

        send_mail(subject, message, 'wishlist@wishlist.pokorny.ca',
                  [user.email], fail_silently=False)
    finally:
        translation.activate(original_language)


def send_weekly_email_for_user(user):
    if not user.email:
        return

    subject = _('This week on the wishlist')
    email = render_weekly_email_for_user(user)

    if not email:
        return

    send_email_to_user(user, subject, email)


def send_occasion_email(occasion):
    user = occasion.user

    to = User.objects.all().exclude(username__in=DUMMY_USERS).exclude(
        username=user.username)

    with user_language('cs'):
        name = occasion.get_name_display()

    for t in to:
        with user_language(t.userprofile.language):
            subject = '%s will have a %s' % (user.first_name, name)
            email = render_to_string('occasion.html', {
                'user': user,
                'occasion': name,
                'DOMAIN': DOMAIN
            })
            send_email_to_user(t, subject, email)

    with user_language(user.userprofile.language):
        email = render_to_string('own-occasion.html', {
            'occasion': name,
            'DOMAIN': DOMAIN
        })
        send_email_to_user(user, subject, email)
