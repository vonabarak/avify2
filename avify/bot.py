# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler
import logging
from avify.settings import TELEGRAM_TOKEN

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self):
        self.updater = Updater(token=TELEGRAM_TOKEN)
        self.dispatcher = self.updater.dispatcher
        # self.dispatcher.add_handler(CommandHandler('start', self.start))
        self.bot = self.updater.bot

    def start_polling(self):
        self.updater.start_polling(timeout=3)

    def stop_polling(self):
        self.updater.stop()

    def msg(self, user, text):
        self.bot.send_message(chat_id=user.tgid, text=text)

    # @staticmethod
    # def start(bot, update):
    #     try:
    #         user, created = User.objects.get_or_create(
    #             username=update.message.from_user.username,
    #             tgid=update.message.from_user.id,
    #             first_name=update.message.from_user.first_name,
    #             last_name=update.message.from_user.last_name,
    #             type=update.message.from_user.type,
    #         )
    #         if created:
    #             message = "U've been successfully registered"
    #         else:
    #             message = "U r already registered"
    #     except BaseException as e:
    #         message = "Something goes wrong. Try again later"
    #         logger.warning(e)
    #     bot.sendMessage(chat_id=update.message.chat_id, text=message)
