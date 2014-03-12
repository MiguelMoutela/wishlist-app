from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/login', 'django.contrib.auth.views.login',
        name='login'),
    url(r'^accounts/logout', 'django.contrib.auth.views.logout',
        {'template_name': 'registration/logout.html'}, name='logout'),
    url(r'^accounts/change', 'django.contrib.auth.views.password_change',
        {'template_name': 'registration/password_change.html',
         'post_change_redirect': '/'},
        name='password-change'),
    url(r'^accounts/change/done$',
        'django.contrib.auth.views.password_change_done',
        {'template_name': 'registration/password_done.html'},
        name='password-change-done'),

    url(r'^$', 'web.views.index', name='index'),
    url(r'^new$', 'web.views.item_create', name='item-create'),
    url(r'^shopping$', 'web.views.shopping', name='shopping'),
    url(r'^list/(?P<username>[0-9a-z]+)$', 'web.views.person_detail',
        name='person-detail'),

    url(r'^item/(?P<pk>[0-9]+)/edit$', 'web.views.item_edit',
        name='item-edit'),

    url(r'^item/(?P<pk>[0-9]+)/enough$', 'web.views.item_enough',
        name='item-enough'),

    url(r'^admin/', include(admin.site.urls)),
)
