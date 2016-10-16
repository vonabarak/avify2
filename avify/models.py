# -*- coding: utf-8 -*-

import logging
from django.db import models
import datetime
from django.utils import timezone
from avify.bot import Bot

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class User(models.Model):
    tgid = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=64, unique=True)
    first_name = models.CharField(max_length=64, unique=False, null=True)
    last_name = models.CharField(max_length=64, unique=False, null=True)
    type = models.CharField(max_length=64, unique=False, null=True)

    def send(self, text):
        bot = Bot()
        bot.bot.send_message(chat_id=self.tgid, text=text)
        bot.updater.stop()


class Proxy(models.Model):
    name = models.CharField(max_length=64)
    port = models.IntegerField()
    login = models.CharField(max_length=128, null=True)
    passwd = models.CharField(max_length=128, null=True)
    priority = models.IntegerField()

    def __str__(self):
        if self.login and self.passwd:
            return 'http://{login}:{passwd}@{name}:{port}'.format(
                    login=self.login,
                    passwd=self.passwd,
                    name=self.name,
                    port=self.port
            )
        else:
            return 'http://{name}:{port}'.format(
                    name=self.name,
                    port=self.port
            )


class SearchCathegory(models.Model):
    name = models.CharField(max_length=512)
    url = models.CharField(max_length=1024)


class Search(models.Model):
    enabled = models.BooleanField(default=True)
    cathegory = models.ForeignKey(SearchCathegory, related_name='searches')
    keywords = models.CharField(max_length=1024)
    price_max = models.IntegerField()
    price_min = models.IntegerField()
    user = models.ForeignKey(User, related_name='searches')
    atime = models.DateTimeField(auto_now=True)
    update_interval = models.IntegerField(default=5)

    @property
    def need_update(self):
        if self.atime + datetime.timedelta(minutes=self.update_interval) > timezone.now():
            return True
        else:
            return False


class ViewedItems(models.Model):
    url = models.CharField(max_length=1024, unique=True)
    ctime = models.DateTimeField(auto_now_add=True)
    search = models.ForeignKey(Search, related_name='viewed_items')
