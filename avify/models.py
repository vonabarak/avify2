# -*- coding: utf-8 -*-

import logging
from django.db import models
from django.contrib.postgres.fields import JSONField
import datetime
from django.utils import timezone
from avify.bot import Bot
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager, Group

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(_('username'), max_length=30, unique=True,
                                help_text=_('Required. 30 characters or fewer. Letters, digits and '
                                            '@/./+/-/_ only.'),
                                validators=[
                                    validators.RegexValidator(r'^[\w.@+-]+$',
                                                              _('Enter a valid username. '
                                                                'This value may contain only letters, numbers '
                                                                'and @/./+/-/_ characters.'), 'invalid'),
                                ],
                                error_messages={
                                    'unique': _("A user with that username already exists."),
                                })
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin '
                                               'site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now, editable=False)
    tgid = models.BigIntegerField(unique=True)
    type = models.CharField(max_length=64, unique=False, null=True)
    auth_token = models.UUIDField(unique=True, null=True)
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['tgid']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return self.username

    def send(self, text):
        bot = Bot()
        bot.bot.send_message(chat_id=self.tgid, text=text)
        bot.updater.stop()


class Search(models.Model):
    cathegory = models.IntegerField(null=False)
    region = models.IntegerField(null=False)
    enabled = models.BooleanField(default=True)
    keywords = models.CharField(max_length=1024)
    price_max = models.IntegerField()
    price_min = models.IntegerField()
    user = models.ForeignKey(User, related_name='searches')
    atime = models.DateTimeField(auto_now=True)
    search_by_description = models.BooleanField(default=False)


class SearchParam(models.Model):
    cathegory = models.IntegerField(null=False)
    name = models.CharField(max_length=1024)
    value = models.CharField(max_length=1024)

    class Meta:
        unique_together = (('cathegory', 'name', 'value'),)


class ViewedItems(models.Model):
    restapp_id = models.BigIntegerField()
    url = models.CharField(max_length=1024)
    avito_id = models.BigIntegerField()
    title = models.TextField()
    price = models.IntegerField()
    time = models.DateTimeField()
    phone = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
    description = models.TextField()
    params = JSONField()
    ctime = models.DateTimeField(auto_now_add=True)
    search = models.ForeignKey(Search, related_name='viewed_items')
    user = models.ForeignKey(User, related_name='viewed_items')

    class Meta:
        unique_together = (('restapp_id', 'user'),)