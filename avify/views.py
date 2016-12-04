# -*- coding: utf-8 -*-

import requests
import logging
import subprocess
import uuid
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.views.generic import FormView, View
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model, logout, login, authenticate
from .forms import *
from avify.models import User, Search, ViewedItems

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class BotWebHookView(View):
    from telegram import Bot
    from telegram.ext import Dispatcher
    from queue import Queue


class HomePageView(FormView):
    template_name = 'home.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        # messages.info(self.request, 'Привет!')
        # logger.critical('Welcome with fortune!')
        fortune = subprocess.Popen(['fortune'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        context['fortune'], _ = fortune.communicate()
        return context

    def get(self, request, *args, **kwargs):
        token = request.GET.get('auth_token', '')
        if token:
            try:
                token_uuid = uuid.UUID(token)
            except ValueError:
                return HttpResponseRedirect(reverse('home'))
            try:
                user = User.objects.get(auth_token=token_uuid)
            except User.DoesNotExist:
                messages.warning(request, _('User doesnt exists or token invalid'))
                return HttpResponseRedirect(reverse('home'))
            login(request, user)
            user.auth_token = None
            user.save()
            logger.info(request, 'User {0} have been logged in with token {1}'.format(user.username, token))
            messages.info(request, _('You have been successfully logged in'))
            return HttpResponseRedirect(reverse('home'))
        else:
            return super(self.__class__, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        token = request.POST.get('auth_token', '')
        if token:
            try:
                token_uuid = uuid.UUID(token)
            except ValueError:
                return HttpResponseRedirect(reverse('home'))
            try:
                user = User.objects.get(auth_token=token_uuid)
            except User.DoesNotExist:
                messages.warning(request, _('User doesnt exists or token invalid'))
                return HttpResponseRedirect(reverse('home'))
            login(request, user)
            user.auth_token = None
            user.save()
            logger.info(request, 'User {0} have been logged in with token {1}'.format(user.username, token))
            messages.info(request, _('You have been successfully logged in'))
            return HttpResponseRedirect(reverse('home'))
        messages.warning(request, _('Login failed'))
        return HttpResponseRedirect(reverse('home'))



class LogoutView(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    @staticmethod
    def get(request):
        messages.info(request, 'Good Bye!')
        logout(request)
        return HttpResponseRedirect(reverse('home'))


class PaginationMixin:
    def __init__(self):
        self.lines = list()
        self.request = None

    def add_paginator(self, context):
        rows = self.request.GET.get('rows', 15)
        paginator = Paginator(self.lines, rows)
        page = self.request.GET.get('page')
        try:
            show_lines = paginator.page(page)
        except PageNotAnInteger:
            show_lines = paginator.page(1)
        except EmptyPage:
            show_lines = paginator.page(paginator.num_pages)
        context['lines'] = show_lines
        context['rows'] = rows
        context['page'] = page



class UsersView(FormView, PaginationMixin):
    template_name = 'users.html'
    form_class = EditUserForm

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        edit_user = self.request.GET.get('edit_user', '')
        if edit_user:
            context['edit_user'] = get_object_or_404(User, id=edit_user)
            context['form'] = self.form_class(instance=context['edit_user'])
        self.lines = User.objects.all()
        self.add_paginator(context)
        return context

    def get(self, request, **kwargs):
        login_as_user = request.GET.get('login_as_user', '')
        if login_as_user:
            try:
                user = User.objects.get(id=int(login_as_user))
                logout(request)
                login(request, user)
            except BaseException as e:
                logger.warning('Exception during logging as another user: {0}'.format(e))
            return HttpResponseRedirect(reverse('home'))
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        user = context['edit_user']
        f = self.form_class(request.POST, instance=user)
        if f.is_valid():
            # If user was not and become active - send a message
            if (not User.objects.get(id=user.id).is_active) and user.is_active:
                user.send('Your account have been approved by administrator. '
                            'Now send me a command "/login" to get login token.')

            if User.objects.get(id=user.id).is_active and not user.is_active:
                user.send('Your account have been disabled by administrator. ')

            f.save()
            messages.info(request, _('Successfylly updated'))
        else:
            messages.info(request, _('Something wrong'))
        return HttpResponseRedirect(reverse('users'))


class SearchesView(FormView, PaginationMixin):
    template_name = 'searches.html'
    form_class = AddSearchForm

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def get_form(self, form_class=None, show_users=False):
        if form_class is None:
            form_class = self.get_form_class()
        if show_users:
            user_choices = [(c.id, u'{}'.format(c.username)) for c in User.objects.all().order_by('id')]
        else:
            user_choices = None
        return form_class(user_choices)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['form'] = self.get_form()

        cathergory = int(self.request.GET.get('cathegory', '0'))
        context['cathegory'] = int(cathergory)
        if cathergory:
            self.lines = Search.objects.filter(cathegory=cathergory, user=self.request.user)
        else:
            self.lines = Search.objects.filter(user=self.request.user).order_by('-id')
        self.add_paginator(context)
        return context

    def post(self, request, *args, **kwargs):
        cathegory = int(request.POST.get('cathegory', '0'))
        region = int(request.POST.get('region', '0'))
        keywords = request.POST.get('keywords', '')
        price_min = int(request.POST.get('price_min', '0'))
        price_max = int(request.POST.get('price_max', '0'))
        search_by_description = bool(request.POST.get('search_by_description', '0'))
        Search.objects.create(
            cathegory=cathegory,
            region=region,
            keywords=keywords,
            price_max=price_max,
            price_min=price_min,
            search_by_description=search_by_description,
            user_id=request.user.id,
        )
        messages.info(request, _('Saved'))
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get(self, request, *args, **kwargs):
        delete = int(request.GET.get('delete', '0'))
        if delete:
            item = get_object_or_404(Search, id=delete)
            if request.user.is_staff or item.user_id == request.user.id:
                item.delete()
                messages.info(request, _('Deleted'))
            else:
                messages.info(request, _('Access denied'))
        return render(request, self.template_name, self.get_context_data(**kwargs))


class ViewedItemsView(TemplateView, PaginationMixin):
    template_name = 'viewed.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        self.lines = ViewedItems.objects.filter(user=self.request.user).order_by('-id')
        self.add_paginator(context)
        return context

class BroadcastMessageView(FormView):
    template_name = 'broadcast_message.html'
    form_class = BroadcastMessageForm

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        msg = request.POST.get('message', '')
        if msg:
            for u in User.objects.filter(is_active=True):
                u.send(msg)
            messages.info(request, _('Message sent'))
        return HttpResponseRedirect(reverse('broadcast'))