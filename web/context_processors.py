from web.models import Item


def fulfilled(request):
    return {
        'fulfilled': Item.objects.filter(already_given=True).count()
    }
