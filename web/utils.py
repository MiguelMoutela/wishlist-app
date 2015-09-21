from datetime import datetime, timedelta
from contextlib import contextmanager

from django.utils import translation
from django.core.mail import send_mail
from django.utils.translation import ugettext as _
from django.conf import settings
from django.template.loader import render_to_string

from models import Buy, Item, users_for_user


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
    # Peers doesn't include self
    peers = users_for_user(user)

    # All of the things that my peers want
    latest_items = Item.objects.filter(user__in=peers).order_by('-created')

    # All of the buys that make peers are making for my peers
    latest_buys = Buy.objects.filter(user__in=peers,
                                     item__in=peers).order_by('-created')

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
    if not user.email:
        return

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

    with user_language(user.userprofile.language):

        subject = _('This week on the wishlist')
        email = render_weekly_email_for_user(user)

        if not email:
            return

        send_email_to_user(user, subject, email)


def send_occasion_email(occasion):
    user = occasion.user

    to = users_for_user(user).exclude(username__in=DUMMY_USERS).exclude(
        username=user.username)

    for t in to:
        with user_language(t.userprofile.language):
            name = occasion.get_name_display()

            subject_filler = _('will have a')
            subject = ' '.join([user.first_name, subject_filler, name])

            email = render_to_string('occasion.html', {
                'user': user,
                'occasion': name,
                'DOMAIN': DOMAIN
            })

            send_email_to_user(t, subject, email)

    with user_language(user.userprofile.language):

        name = occasion.get_name_display()
        subject = ' '.join([_('You will have a'), name])
        email = render_to_string('own-occasion.html', {
            'occasion': name,
            'DOMAIN': DOMAIN
        })
        send_email_to_user(user, subject, email)
