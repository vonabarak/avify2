# -*- coding: utf-8 -*-

import requests
import subprocess
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.shortcuts import render
from .forms import *
from avify.models import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)

        # messages.info(self.request, 'Привет!')
        logger.critical('Welcome with fortune!')
        fortune = subprocess.Popen(['fortune'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        context['fortune'], _ = fortune.communicate()
        return context


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



class UsersView(TemplateView, PaginationMixin):
    template_name = 'users.html'

    def dispatch(self, *args, **kwargs):
        return super(self.__class__, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        self.lines = User.objects.all()
        self.add_paginator(context)
        return context


class ProxyView(FormView):
    template_name = 'proxies.html'
    form_class = AddProxyForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        lines = Proxy.objects.all()
        rows = self.request.GET.get('rows', 15)
        paginator = Paginator(lines, rows)
        page = self.request.GET.get('page')
        try:
            show_lines = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_lines = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            show_lines = paginator.page(paginator.num_pages)
        context['lines'] = show_lines
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '')
        port = int(request.POST.get('port', '0'))
        prio = int(request.POST.get('prio', '0'))
        login = request.POST.get('login', '')
        passwd = request.POST.get('passwd', '')
        proxy = Proxy()
        proxy.name = name
        proxy.port = port
        proxy.priority = prio
        if login:
            proxy.login = login
        if passwd:
            proxy.passwd = passwd
        proxy.save()
        messages.info(request, 'Saved')
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get(self, request, *args, **kwargs):
        delete = int(request.GET.get('delete', '0'))
        check = int(request.GET.get('check', '0'))
        if delete:
            proxy = Proxy.objects.get(id=delete)
            proxy.delete()
            messages.info(request, 'Deleted')
        elif check:
            p = Proxy.objects.get(id=check)
            ok = False
            try:
                response = requests.get('https://www.avito.ru', proxies={'https': str(p)})
                if response.status_code == requests.codes.ok:
                    ok = True
            except BaseException as e:
                logger.warning('Proxy is not working with exception {0}'.format(e))

            if ok:
                messages.info(request, 'Proxy {} works!'.format(p.name))
            else:
                messages.warning(request, 'Proxy {} DOES NOT works!'.format(p.name))

        return render(request, self.template_name, self.get_context_data(**kwargs))


class CathegoriesView(FormView, PaginationMixin):
    template_name = 'cathegories.html'
    form_class = AddSearchCathegoryForm

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        context['form'] = self.form_class()
        self.lines = SearchCathegory.objects.all()
        self.add_paginator(context)
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '')
        url = request.POST.get('url', '')
        cath = SearchCathegory()
        cath.name = name
        cath.url = url
        cath.save()
        messages.info(request, 'Saved')
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get(self, request, *args, **kwargs):
        delete = int(request.GET.get('delete', '0'))
        if delete:
            cath = SearchCathegory.objects.get(id=delete)
            cath.delete()
            messages.info(request, 'Deleted')
        return render(request, self.template_name, self.get_context_data(**kwargs))


class SearchesView(FormView, PaginationMixin):
    template_name = 'searches.html'
    form_class = AddSearchForm

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        cathegory_choices = [
            (c.id, u'{}'.format(c.name)) for c in SearchCathegory.objects.all()
            ]
        user_choices = [
            (c.id, u'{}'.format(c.username)) for c in User.objects.all().order_by('id')
            ]
        return form_class(cathegory_choices, user_choices)

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        # context['form'] = self.get_form()
        self.lines = Search.objects.all().order_by('-id')
        self.add_paginator(context)
        return context

    def post(self, request, *args, **kwargs):
        cathegory = int(request.POST.get('cathegory', '0'))
        keywords = request.POST.get('keywords', '')
        price_min = int(request.POST.get('price_min', '0'))
        price_max = int(request.POST.get('price_max', '0'))
        user_id = int(request.POST.get('user', '0'))
        search = Search()
        search.cathegory = SearchCathegory.objects.get(id=cathegory)
        search.keywords = keywords
        search.price_max = price_max
        search.price_min = price_min
        search.user_id = user_id
        search.save()
        messages.info(request, 'Saved')
        return render(request, self.template_name, self.get_context_data(**kwargs))

    def get(self, request, *args, **kwargs):
        delete = int(request.GET.get('delete', '0'))
        if delete:
            cath = Search.objects.get(id=delete)
            cath.delete()
            messages.info(request, 'Deleted')
        return render(request, self.template_name, self.get_context_data(**kwargs))


class ViewedItemsView(TemplateView, PaginationMixin):
    template_name = 'viewed.html'

    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        self.lines = ViewedItems.objects.all().order_by('-id')
        self.add_paginator(context)
        return context
