from celery.schedules import crontab
from celery.task import periodic_task, task
from django.contrib.auth.models import User

from utils import (
    send_weekly_email_for_user, send_weekly_nagging_email_for_user,
    get_users_to_notify_of_new_item, send_new_item_notification_email
)
from models import Occasion, get_users_to_nag, Item


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


@periodic_task(run_every=crontab(hour=20, minute=0, day_of_week=5))
def send_nagging_emails():
    for user in get_users_to_nag():
        send_weekly_nagging_email_for_user(user)


@task
def send_new_item_notification_emails(item_pk):
    print 'in task'
    users = get_users_to_notify_of_new_item(item_pk)

    try:
        item = Item.objects.get(pk=item_pk)
    except Item.DoesNotExist:
        print 'nope'
        return

    for user in users:
        print user
        send_new_item_notification_email(item, user)
