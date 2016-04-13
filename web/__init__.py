import django_rq
from django.contrib.auth.models import User

from utils import (
    send_weekly_email_for_user, send_weekly_nagging_email_for_user
)
from models import Occasion, get_users_to_nag


scheduler = django_rq.get_scheduler('default')


def send_emails():
    for user in User.objects.all():
        send_weekly_email_for_user(user)


def send_occasion_emails():
    """
    Daily at 8pm
    """
    from utils import send_occasion_email
    for o in Occasion.objects.in_2_weeks():
        send_occasion_email(o)


def send_nagging_emails():
    for user in get_users_to_nag():
        send_weekly_nagging_email_for_user(user)


scheduler.cron(
    '0 19 * * 1',
    func=send_emails
)


scheduler.cron(
    '0 20 * * *',
    func=send_occasion_emails
)


scheduler.cron(
    '0 20 * * 5',
    func=send_nagging_emails
)
