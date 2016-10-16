from django.core.management.base import BaseCommand  # CommandError
from avify.parse import Parser


class Command(BaseCommand):
    args = '[]'
    help = ''

    def handle(self, *args, **kwargs):
        Parser().get_items()

