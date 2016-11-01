# -*- coding: utf-8 -*-

from avify.models import Proxy, ViewedItems, SearchCathegory
import logging
import requests
import re
from bs4 import BeautifulSoup

requests.packages.urllib3.disable_warnings()  # suppress noisy messages

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def normalize_price(text):
    try:
        return float(''.join([ch for ch in text if ch.isdigit()]))
    except ValueError:
        return 0.0


class Parser:
    def __init__(self):
        self.proxies = Proxy.objects.order_by('priority').all()
        # for p in self.proxies:
        #     print(p.name)

    def get_items(self):
        logger.warning('Start parsing.')
        for cath in SearchCathegory.objects.all():
            logger.info(u'Cathegory: {0}'.format(cath.name))
            for p in self.proxies:
                try:
                    # print(u'Trying proxy {}'.format(p))
                    r = requests.get(cath.url, proxies={'https': str(p)})
                    if r.status_code == requests.codes.ok:
                        parsed_body = BeautifulSoup(r.text, 'html.parser')
                        for page_elem in parsed_body.body.findAll('div', attrs={'class': 'description'}):
                            url = page_elem.find('a').get('href')
                            price = normalize_price(page_elem.find('div', attrs={'class': 'about'}).get_text())
                            logger.debug(url)
                            for srch in cath.searches.all():
                                if re.search(srch.keywords, page_elem.text.lower()):
                                    if ViewedItems.objects.filter(url=url):
                                        logger.debug(u'{0} already viewed'.format(url))
                                        continue
                                    if price > srch.price_max:
                                        logger.debug(u'{0} too expensive'.format(url))
                                        continue
                                    if price < srch.price_min:
                                        logger.debug(u'{0} too cheap'.format(url))
                                        continue
                                    logger.info(u'Found {0}'.format(url))
                                    srch.user.send(u'{1} Руб. https://avito.ru{0}'.format(
                                        url,
                                        price
                                    ))
                                    v = ViewedItems(url=url, search=srch)
                                    v.save()

                    else:
                        continue
                    break
                except BaseException as e:
                    logger.error(e)
                    continue
