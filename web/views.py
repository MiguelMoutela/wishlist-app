from datetime import datetime, timedelta

from django.db import transaction
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from models import (
    Buy, Item, users_for_user, UserProfile, MagicLink,
    MagicLinkClick
)
from forms import ItemForm, ContributionForm
from utils import get_latest_for_user
from tasks import send_new_item_notification_emails


DUMMY_USERS = getattr(settings, 'DUMMY_USERS', [])
DEBUG = getattr(settings, 'DEBUG', True)

HIDE = _('Hide taken')
SHOW = _('Show taken')


@login_required
def index(request):
    heading = _('Welcome')
    items = Item.objects.filter(user=request.user,
                                already_given=False,
                                surprise=False).order_by('created')

    user_objs = users_for_user(request.user).order_by('first_name')
    users = []

    for user in user_objs:
        user_items = user.item_set.filter(already_given=False)
        items_count = user_items.count()

        if DEBUG:
            buy_count = 0
        else:
            buy_count = Buy.objects.filter(
                item__in=user_items).distinct('item').count()

        free = user_items.count() - buy_count

        users.append({
            'user': user,
            'count': items_count,
            'free': free
        })

    if request.user.username in DUMMY_USERS:
        latest = []
    else:
        latest = get_latest_for_user(request.user)

    data = {
        'items': items,
        'heading': heading,
        'users': users,
        'latest': latest[:10]
    }
    return render(request, 'index.html', data)


@login_required
@transaction.atomic
def item_create(request, user_pk=None):
    # NOTE: If user_pk is not None, then we're adding a surprise

    # You can't add a surprise for yourself
    if user_pk is not None and int(user_pk) == request.user.pk:
        raise Http404

    surprise = user_pk is not None

    # If it's a surprise, we need to know who the target is.
    if surprise:
        user = get_object_or_404(User, pk=user_pk)
    else:
        user = None

    if request.method == 'POST':

        if not user:
            user = request.user

        form = ItemForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = user
            obj.surprise = surprise
            obj.created_by = request.user
            obj.save()

            send_new_item_notification_emails.delay(obj.pk)

            if surprise:
                buy = Buy.objects.create(user=request.user, item=obj)
                buy.save()
                return redirect('person-detail', obj.user.username)

            return redirect('index')
    else:
        form = ItemForm()

    data = {
        'form': form,
        'current_user': user
    }
    return render(request, 'new.html', data)


@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.user.pk != request.user.pk:
        raise Http404

    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save(commit=True)
            messages.success(request, _("Saved"))
            return redirect('/')
    else:
        form = ItemForm(instance=item)

    data = {
        'form': form,
        'edit': True
    }

    return render(request, 'new.html', data)


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.user.pk != request.user.pk:
        raise Http404

    if request.method == 'POST':
        item.delete()
        messages.success(request, _("Deleted"))
        return redirect('/')

    data = {
        'item': item
    }

    return render(request, 'delete.html', data)


@login_required
def item_given(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.user.pk != request.user.pk:
        raise Http404

    if request.method == 'POST':
        item.already_given = True
        item.save()
        messages.success(request, _("Saved"))
        return redirect('/')

    data = {
        'item': item
    }

    return render(request, 'given.html', data)


@login_required
def item_enough(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.user.pk != request.user.pk:
        raise Http404

    if request.method == 'POST':
        if not item.multi_item:
            raise Http404

        item.already_given = True
        item.save()
        messages.success(request, _("Saved"))

    return redirect('index')


@login_required
def person_detail(request, username):
    person = get_object_or_404(User, username=username)

    if person.pk == request.user.pk:
        raise Http404

    if request.user.username in DUMMY_USERS:
        raise Http404

    if request.method == 'POST':
        item_pk = request.POST.get('item')
        item = get_object_or_404(Item, pk=item_pk)
        action = request.POST.get('action', None)

        buying = item.buying

        if not action:
            pass

        if action == 'add':
            if buying and not item.multi_item:
                raise Http404

            Buy.objects.create(user=request.user, item=item)

            messages.success(request, _("You've committed to buy an item."))
            return redirect('person-detail', username=username)

        if action == 'remove':
            if not buying:
                raise Http404

            Buy.objects.filter(user=request.user, item=item).delete()

            if item.price and not Buy.objects.filter(item=item).exists():
                item.price = None
                item.save()
                messages.success(request, _("You've been removed."))

            elif item.surprise:
                item.delete()
                messages.success(request, _("Deleted"))
            else:
                messages.success(request, _("Done!"))

            return redirect('person-detail', username=username)

    items = Item.objects.filter(
        user=person, already_given=False).order_by('created')

    data = {
        'person': person,
        'items': items,
        'my_buying': Item.objects.filter(buy__user=request.user),
        'HIDE': HIDE,
        'SHOW': SHOW
    }
    return render(request, 'person-detail.html', data)


@login_required
def shopping(request):
    if request.method == 'POST':
        action = request.POST.get('action', None)

        if not action:
            raise Http404

        if action == 'given':

            pk = request.POST.get('item_pk', None)

            if not pk:
                raise Http404

            item = get_object_or_404(Item, pk=pk)

            if item.multi_item:
                raise Http404

            item.already_given = True
            item.save()

        if action == 'purchase':

            pk = request.POST.get('buy_pk', None)

            if not pk:
                raise Http404

            buy = get_object_or_404(Buy, pk=pk)
            buy.purchased = True
            buy.save()

        if action == 'unpurchase':

            pk = request.POST.get('buy_pk', None)

            if not pk:
                raise Http404

            buy = get_object_or_404(Buy, pk=pk)
            buy.purchased = False
            buy.save()

        messages.success(request, _("Saved"))
        return redirect('shopping')

    else:
        items = Buy.objects.filter(user=request.user,
                                   item__already_given=False)

        to_purchase = items.filter(purchased=False)
        purchased = items.filter(purchased=True)

        data = {
            'to_purchase': to_purchase,
            'purchased': purchased
        }
        return render(request, 'shopping.html', data)


@login_required
def contribute(request, pk):
    item = get_object_or_404(Item, pk=pk)

    contribution = None
    buy = None
    if Buy.objects.filter(user=request.user, item=item).exists():
        buy = Buy.objects.get(user=request.user, item=item)
        contribution = buy.amount

    if request.method == 'POST':
        form = ContributionForm(request.POST)
        if form.is_valid():
            item.price = form.cleaned_data["estimation"]
            item.save()

            if not buy:
                buy = Buy()

            buy.user = request.user
            buy.item = item
            buy.amount = form.cleaned_data["contribution"]
            buy.save()
            messages.success(request, _("Saved"))
            return redirect('person-detail', item.user.username)
    else:
        form = ContributionForm(initial={
            'estimation': item.price, 'contribution': contribution})

    data = {
        'form': form,
        'item': item
    }
    return render(request, 'contribution.html', data)


def unsubscribe(request, uuid):
    profile = get_object_or_404(UserProfile, uuid=uuid)

    profile.subscribed_to_email = False
    profile.save()

    return render(request, 'unsubscribed.html', {})


def visits(request):
    users = User.objects.all().order_by('username')
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    day_ago = now - timedelta(hours=24)

    visits = []

    for user in users:
        if user.username in DUMMY_USERS:
            continue

        last_week = user.visit_set.filter(created__lt=now,
                                          created__gt=week_ago).count()
        last_day = user.visit_set.filter(created__lt=now,
                                         created__gt=day_ago).count()
        total = user.visit_set.all().count()

        visits.append({
            'user': user,
            'last_week': last_week,
            'last_day': last_day,
            'total': total
        })

    data = {
        'visits': visits
    }

    return render(request, 'visits.html', data)


def magic(request, uuid):
    link = get_object_or_404(MagicLink, uuid=uuid)
    user = link.user
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    MagicLinkClick.objects.create(link=link)
    login(request, link.user)

    next = request.GET.get('next')

    if next:
        return redirect(next)

    return redirect('index')
