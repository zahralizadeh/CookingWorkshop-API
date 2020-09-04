# -*- coding: utf-8 -*-
import json
import logging

import scrapy
from scrapy_app.items import CategoryItem

logger = logging.getLogger(__name__)


class CookingworkshopCategorySpider(scrapy.Spider):
    name = 'cookingworkshop_category'
    url = 'http://www.cheftayebeh.ir/feeds/posts/summary?start-index=1&max-results=150&alt=json'

    def start_requests(self):
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        if response.status != 200:
            logger.error("-----Can not retrive page!")
            return

        body = response.body.decode(response.encoding)

        try:
            data = json.loads(body)
        except ValueError:
            logger.error("-----Error in parsing json file")
            return

        categories = data['feed']['category']
        for category in categories:
            yield self.fill_category_item(category)

    def fill_category_item(self, category):
        """
        returns CategoryItem
        """
        item = CategoryItem()
        item['title_fa'] = category['term']
        item['title_en'] = ""
        return item
