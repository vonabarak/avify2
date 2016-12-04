# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
import logging
from django.contrib.auth import get_user_model
from uuid import uuid4
from avify.settings import TELEGRAM_TOKEN

logger = logging.getLogger(__name__)

class Bot:
    def __init__(self):
        self.updater = Updater(token=TELEGRAM_TOKEN)
        self.dispatcher = self.updater.dispatcher
        self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.dispatcher.add_handler(CommandHandler('login', self.token))
        self.bot = self.updater.bot

    def start_polling(self):
        self.updater.start_polling(timeout=3)

    def stop_polling(self):
        self.updater.stop()

    def msg(self, user, text):
        self.bot.send_message(chat_id=user.tgid, text=text)

    @staticmethod
    def start(bot, update):
        try:
            user_model = get_user_model()
            user, created = user_model.objects.get_or_create(
                username=update.message.from_user.username,
                tgid=update.message.from_user.id,
                first_name=update.message.from_user.first_name,
                last_name=update.message.from_user.last_name,
                type=update.message.from_user.type,
                is_active=False
            )
            if created:
                message = "You've been successfully registered. Please, wait for administrators approve."
            else:
                message = "You are already registered."
        except BaseException as e:
            message = "Something goes wrong. Try again later"
            logger.warning(e)
        bot.sendMessage(chat_id=update.message.chat_id, text=message)

    @staticmethod
    def token(bot, update):
        try:
            user_model = get_user_model()
            user = user_model.objects.get(tgid=update.message.from_user.id)

            token = uuid4()
            user.auth_token = token
            user.save()
            message = 'Your authentication token is:\n' \
                      '{0}\n' \
                      'Copy and paste it into login form or just follow this link\n' \
                      'https://avify.ru/?auth_token={0}' \
                      ''.format(token)
            logger.error(user.id)
            logger.error(user.auth_token)
            logger.error(user_model.objects.get(id=user.id).auth_token)
        except BaseException as e:
            message = "Something goes wrong. Try again later"
            logger.warning(e)
        bot.sendMessage(chat_id=update.message.chat_id, text=message)
