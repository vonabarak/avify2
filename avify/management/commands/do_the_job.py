from django.core.management.base import BaseCommand  # CommandError
from avify.restapp import Restapp


class Command(BaseCommand):
    args = '[]'
    help = ''

    def handle(self, *args, **kwargs):
        Restapp().do_the_job()

