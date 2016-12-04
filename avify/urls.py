# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from avify.views import *

admin.autodiscover()

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    url(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^$', HomePageView.as_view(), name='home'),

    url(r'^users$', UsersView.as_view(), name='users'),
    url(r'^searches$', SearchesView.as_view(), name='searches'),
    url(r'^viewed$', ViewedItemsView.as_view(), name='viewed'),

    url(r'^bot_webhook$', BotWebHookView.as_view(), name='bot_webhook'),

    url(r'^broadcast$', BroadcastMessageView.as_view(), name='broadcast'),
]
