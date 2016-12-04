# -*- coding: utf-8 -*-

import signal
from django.core.management.base import BaseCommand
from avify.bot import Bot, logger

class Command(BaseCommand):
    help = ''
    args = '[]'

    bot = Bot()

    def signal_handler(self, sig, frame):
        logger.info('Stopping poller, {0}, {1}'.format(sig, frame))
        self.bot.stop_polling()

    def handle(self, *args, **kwargs):
        signal.signal(signal.SIGINT, self.signal_handler)
        try:
            self.bot.start_polling()
        except IOError as e:
            logger.error(e)