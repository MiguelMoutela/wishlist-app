from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from models import Buy, Item
from forms import ItemForm, ContributionForm
from utils import get_latest_for_user


DUMMY_USERS = getattr(settings, 'DUMMY_USERS', [])


@login_required
def index(request):
    heading = _('Welcome')
    items = Item.objects.filter(user=request.user,
                                already_given=False,
                                surprise=False).order_by('created')

    user_objs = User.objects.exclude(pk=request.user.pk).order_by('first_name')
    users = []

    for user in user_objs:
        users.append({
            'user': user,
            'count': user.item_set.filter(already_given=False).count()
        })

    latest = get_latest_for_user(request.user)

    data = {
        'items': items,
        'heading': heading,
        'users': users,
        'latest': latest[:10]
    }
    return render_to_response('index.html', data,
                              context_instance=RequestContext(request))


@login_required
def item_create(request, user_pk=None):
    if user_pk is not None and int(user_pk) == request.user.pk:
        raise Http404

    user = None
    if user_pk is not None:
        user = get_object_or_404(User, pk=user_pk)

    if request.method == 'POST':
        surprise = True
        if user is None:
            user = request.user
            surprise = False

        form = ItemForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = user
            obj.surprise = surprise
            obj.save()
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
    return render_to_response('new.html', data,
                              context_instance=RequestContext(request))


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

    return render_to_response('new.html', data,
                              context_instance=RequestContext(request))


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

    return render_to_response('delete.html', data,
                              context_instance=RequestContext(request))


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
            return redirect('person-detail', username=username)

    data = {
        'person': person,
        'items': Item.objects.filter(user=person, already_given=False),
        'myBuying': Item.objects.filter(buy__user=request.user)
    }
    return render_to_response('person-detail.html', data,
                              context_instance=RequestContext(request))


@login_required
def shopping(request):
    if request.method == 'POST':
        pk = request.POST.get('item_pk', None)

        if not pk:
            raise Http404

        item = get_object_or_404(Item, pk=pk)

        if item.multi_item:
            raise Http404

        item.already_given = True
        item.save()

        messages.success(request, _("Saved"))
        return redirect('shopping')

    else:
        items = Buy.objects.filter(user=request.user)
        buying_items = []

        for b in items:
            if b.item.already_given:
                continue

            buying_items.append(b.item)

        data = {
            'items': buying_items
        }
        return render_to_response('shopping.html', data,
                                  context_instance=RequestContext(request))


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
    return render_to_response('contribution.html', data,
                              context_instance=RequestContext(request))
