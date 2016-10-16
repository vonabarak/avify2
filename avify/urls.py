# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from avify.views import *

admin.autodiscover()

urlpatterns = [
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    url(r'^admin/', include(admin.site.urls), name='admin'),
    # url(r'^accounts/login/$', LoginView.as_view(), name='login'),
    # url(r'^accounts/logout/$', LogoutView.as_view(), name='logout'),
    url(r'^$', HomePageView.as_view(), name='home'),

    url(r'^users$', UsersView.as_view(), name='users'),
    # url(r'^sendmessage$', SendMessageView.as_view(), name='sendmessage'),
    # url(r'^edituser$', EditUserView.as_view(), name='edituser'),
    # url(r'^adduser$', AddUserView.as_view(), name='adduser'),
    url(r'^proxies$', ProxyView.as_view(), name='proxies'),
    url(r'^cathegories$', CathegoriesView.as_view(), name='cathegories'),
    url(r'^searches$', SearchesView.as_view(), name='searches'),
    url(r'^viewed$', ViewedItemsView.as_view(), name='viewed'),
]
