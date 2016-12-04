# -*- coding: utf-8 -*-

from avify.models import ViewedItems, Search, SearchParam
import logging
import requests
import traceback
import re
import urllib
import datetime
from avify.settings import RESTAPP


requests.packages.urllib3.disable_warnings()  # suppress noisy messages

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Restapp:
    def __init__(self):
        self.token = RESTAPP['token']
        self.login = RESTAPP['login']
        self.password = RESTAPP['password']
        self.url = 'http://rest-app.net/api/ads?login={0}&token={1}'.format(self.login, self.token)

    def process_search(self, search):
        url = self.url + \
              '&category_id={cathegory}' \
              '&region_id={region}' \
              '&last_m={update_interval}' \
              '&price1={price_min}' \
              '&price2={price_max}' \
              ''.format(
                  cathegory=search.cathegory,
                  region=search.region,
                  update_interval=2,
                  price_min=search.price_min,
                  price_max=search.price_max
              )
        try:
            response = requests.get(url).json()
        except BaseException as e:
            logger.error(e)
            return None
        for i in response['data']:
            if ViewedItems.objects.filter(user=search.user, restapp_id=i['Id']):
                logger.debug('{0} already viewed by {1}'.format(i['Id'], search.user.username))
                continue
            if not re.search(search.keywords, i['title'].lower()):
                continue
            if search.search_by_description and not re.search(search.keywords, i['description'].lower()):
                continue
            item = ViewedItems(
                restapp_id=int(i['Id']),
                url=i['url'],
                avito_id=int(i['avito_id']),
                title=i['title'],
                price=int(i['price']),
                time=datetime.datetime.strptime(i['time'], '%Y-%m-%d %H:%M:%S'),
                phone=i['phone'],
                name=i['name'],
                description=i['description'],
                params=i['params'],
                search=search,
                user=search.user
            )
            item.save()

            # saving search params
            learn_search_params = False
            if learn_search_params and 'params' in i:
                for p in i['params']:
                    _, created = SearchParam.objects.get_or_create(
                        cathegory=search.cathegory,
                        name=p['name'],
                        value=p['value']
                    )
                    if created:
                        logger.debug('Search param created')
            search.user.send(
                'Search id: {0}\n'
                'URL: {1}\n'
                'price: {2}\n'
                'name: {3}\n'
                'phone: {4}'
                ''.format(i['Id'], item.url, item.price, item.name, item.phone)
            )

    def do_the_job(self):
        for i in Search.objects.filter(enabled=True, user__is_active=True):
            logger.debug('Updating iterms for search template id {0}'.format(i.id))
            try:
                if i.enabled:
                    self.process_search(i)
                else:
                    logger.debug('Search template {0} is disabled.'.format(i.id))
            except BaseException as e:
                logger.error('An error occurred while processing search {0}:\n{1}'.format(i.id, e))