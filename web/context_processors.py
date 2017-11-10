from django.conf import settings
from web.models import Item


def fulfilled(request):
    return {
        'fulfilled': Item.objects.filter(already_given=True).count()
    }


def version(request):
    return {
        'VERSION': getattr(settings, 'VERSION', 'dev')
    }
