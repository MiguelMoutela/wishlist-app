from celery.schedules import crontab
from celery.task import periodic_task
from django.contrib.auth.models import User

from utils import (
    send_weekly_email_for_user, send_weekly_nagging_email_for_user
)
from models import Occasion


@periodic_task(run_every=crontab(hour=19, minute=0, day_of_week=1))
def send_emails():
    for user in User.objects.all():
        send_weekly_email_for_user(user)


@periodic_task(run_every=crontab(hour=20, minute=0))
def send_occasion_emails():
    """
    Daily at 8pm
    """
    from utils import send_occasion_email
    for o in Occasion.objects.in_2_weeks():
        send_occasion_email(o)


@periodic_task(run_every=crontab(hour=19, minute=0, day_of_week=5))
def send_nagging_emails():
    for user in User.objects.all():
        item_count = user.item_set.filter(already_given=False).count()

        if item_count == 0:
            send_weekly_nagging_email_for_user(user)
