from celery.schedules import crontab
from celery.task import periodic_task
from django.contrib.auth.models import User

from utils import send_weekly_email_for_user


@periodic_task(run_every=crontab(hour=19, minute=0, day_of_week=1))
def send_emails():
    for user in User.objects.all():
        send_weekly_email_for_user(user)
