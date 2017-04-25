# -*- coding: utf-8 -*-
import re
import os
import django
import scrapy
import requests
import json
import datetime
from os import sys, path
from scrapy.selector import Selector

sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(path.abspath(__file__))))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "walmart_site.settings")
django.setup()

from product.models import *
from product.views import *

class WalmartSpider(scrapy.Spider):
    name = "walmart"

    custom_settings = {
        'USER_AGENT': 'walmart_scraper (+http://www.yourdomain.com)',
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_IP': 8,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,
        'AUTOTHROTTLE_MAX_DELAY': 60,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'AUTOTHROTTLE_DEBUG': False
    }

    def __init__(self, task_id):
        self.task = ScrapyTask.objects.get(id=int(task_id))

        if self.task.mode == 1:
            set_old_category_products(self.task.category)
            if self.task.category.url == '/':
                self.categories = get_subcategories()
                self.excludes = [item.url for item in Product.objects.all()]
            else:
                self.categories = [self.task.category.url]
                self.excludes = get_category_products(self.categories[0])
        elif self.task.mode == 2:
            self.products = Product.objects.filter(id__in=get_ids(self.task.products))
            self.excludes = [item.url for item in self.products]

    def start_requests(self):    
        if self.task.mode == 1:
            cate_requests = []
            for item in self.categories:
                request = scrapy.Request('https://www.walmart.com'+item,
                                          callback=self.parse)
                request.meta['category'] = item
                # request.meta['proxy'] = 'http://'+random.choice(self.proxy_pool)
                cate_requests.append(request)
            return cate_requests
        else:
            product_requests = []
            for product in self.products:
                request = scrapy.Request('https://www.walmart.com'+product.category_id, 
                                         callback=self.parse)
                # request.meta['category'] = product.category_id
                product_requests.append(request)
            return product_requests    

    def closed(self, reason):
        self.update_run_time()
        # self.store_report()

    def parse(self, response):
        if self.stop_scrapy():
            return

        script = response.xpath("//script[contains(text(), 'window.__WML_REDUX_INITIAL_STATE__ = ')]")[0]
        script = script.xpath("text()").extract_first()
        if not script:
            return
        content = json.loads(script.split("window.__WML_REDUX_INITIAL_STATE__ = ")[1][0:-1])
        products = []
        cates_url = []
        cates_title = []

        try:
            item = content['presoData']['modules']['left'][0]
            if item['moduleTitle'] == "Shop by Category":
                for item_ in item['data']:
                    cates_url.append(item_['url'])
                    cates_title.append(item_['title'])
        except Exception, e:
            print str(e), '@@@@@@@@@@'

        try:
            products = content['preso']['items']
        except Exception, e:
            print str(e), '###########'

        if cates_url:
            parent = response.meta['category']
            for item in zip(cates_url, cates_title):
                url = item[0].split('?')[0]
                if not Category.objects.filter(url=url):
                    Category.objects.create(parent_id=parent, url=url, title=item[1])

                    request = scrapy.Request('https://www.walmart.com'+url, callback=self.parse)
                    request.meta['category'] = url
                    # request.meta['proxy'] = 'http://'+random.choice(self.proxy_pool)
                    yield request
        elif products:
            for product in products:
                url = 'https://www.walmart.com' + product['productPageUrl']
                url = url.split('?')[0]
                if (self.task.mode == 1 and not url in self.excludes) or (self.task.mode == 2 and url in self.excludes):
                    category = response.url.split('?')[0][23:]
                    promo = ''
                    price = ''
                    special = ''
                    delivery_time = ''

                    if product['primaryOffer'].get('offerPrice'):
                        price = '${}'.format(product['primaryOffer']['offerPrice'])
                    elif product['primaryOffer'].get('minPrice'):
                        price = '${} - ${}'.format(product['primaryOffer']['minPrice'], product['primaryOffer']['maxPrice'])

                    special = product.get('specialOfferText', '')
                    if 'listPrice' in product['primaryOffer']:
                        promo = '$' + str(product['primaryOffer']['listPrice'])
                    if 's2HDisplayFlags' in product['fulfillment']:
                        promo += '\n' + '\n'.join(product['fulfillment']['s2HDisplayFlags'])
                    if 's2SDisplayFlags' in product['fulfillment']:
                        promo += '\n' + '\n'.join(product['fulfillment']['s2SDisplayFlags'])
                    if product.get('twoDayShippingEligible', ''):
                        delivery_time = '2-Day Shipping'

                    try:
                        item = {
                            'id': product['usItemId'],
                            'title': product['title'],
                            'price': price,
                            'picture': product['imageUrl'],
                            'rating': product.get('customerRating', 0),
                            'review_count': product.get('numReviews', 0),
                            'promo': promo,
                            'category_id': category,
                            'delivery_time': delivery_time,
                            'bullet_points': '',
                            'details': product.get('description', '').replace('<li>', '').replace('</li>', '\n'),
                            'quantity': product.get('quantity', 0),
                            'min_quantity': 1,
                            'special': special,
                            'url': url
                        }    

                        Product.objects.update_or_create(id=item['id'], defaults=item)
                        yield item    
                    except Exception, e:
                        print str(e), '@@@@@@@@@@@@@@@@'
                        print product

            # for other pages / pagination
            offset = response.meta.get('offset', 1)
            total_records = response.meta.get('total_records', content["preso"]["requestContext"]["itemCount"]["total"])
            
            if offset * 40 < total_records:
                offset += 1 # page
                base_url = response.url.split('?')[0]
                next_url = base_url+'?page={}'.format(offset)
                request = scrapy.Request(next_url, callback=self.parse)
                request.meta['offset'] = offset
                request.meta['total_records'] = total_records
                yield request    

    def update_run_time(self):
        self.task.last_run = datetime.datetime.now()
        self.task.status = 2 if self.task.mode == 2 else 0       # Sleeping / Finished
        self.task.update()

    def store_report(self):
        if self.task.mode == 1:
            result = []
            for cate in self.task.category.get_all_children():
                # only for new products
                for item in Product.objects.filter(category=cate, 
                                                   is_new=True):
                    result.append(item)
        else:
            result = Product.objects.filter(id__in=get_ids(self.task.products))

        fields = [f.name for f in Product._meta.get_fields() 
                  if f.name not in ['updated_at', 'is_new']]

        date = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        path = '/home/exports/walmart-{}-{}.csv'.format(self.task.title, date)
        write_report(result, path, fields)

    def stop_scrapy(self):
        st = ScrapyTask.objects.filter(id=self.task.id).first()
        return not st or st.status == 3
