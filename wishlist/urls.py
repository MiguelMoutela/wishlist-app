from django.conf.urls import include, url
from web.forms import WishlistAuthenticationForm
from django.contrib.auth.views import (
    login, logout, password_change, password_change_done
)

from web import views

from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^accounts/login', login,
        {'authentication_form': WishlistAuthenticationForm},
        name='login'),
    url(r'^accounts/logout', logout,
        {'template_name': 'registration/logout.html'}, name='logout'),
    url(r'^accounts/change', password_change,
        {'template_name': 'registration/password_change.html',
         'post_change_redirect': '/'},
        name='password-change'),
    url(r'^accounts/change/done$', password_change_done,
        {'template_name': 'registration/password_done.html'},
        name='password-change-done'),

    url(r'^unsubscribe/(?P<uuid>[a-zA-Z0-9]+)/$', views.unsubscribe,
        name='unsubscribe'),

    url(r'^magic/(?P<uuid>[a-zA-Z0-9]+)/$', views.magic,
        name='magic'),

    url(r'^$', views.index, name='index'),
    url(r'^new$', views.item_create, name='item-create'),
    url(r'^new/(?P<user_pk>[0-9]+)$', views.item_create, name='item-create'),
    url(r'^shopping$', views.shopping, name='shopping'),
    url(r'^list/(?P<username>[0-9a-z]+)$', views.person_detail,
        name='person-detail'),

    url(r'^item/(?P<pk>[0-9]+)/edit$', views.item_edit,
        name='item-edit'),
    url(r'^item/(?P<pk>[0-9]+)/delete$', views.item_delete,
        name='item-delete'),
    url(r'^item/(?P<pk>[0-9]+)/given$', views.item_given,
        name='item-given'),

    url(r'^item/(?P<pk>[0-9]+)/enough$', views.item_enough,
        name='item-enough'),

    url(r'^item/(?P<pk>[0-9]+)/contribute$', views.contribute,
        name='contribute'),

    url(r'^visits$', views.visits),

    url(r'^admin/', admin.site.urls),
]
