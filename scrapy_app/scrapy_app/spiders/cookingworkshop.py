# -*- coding: utf-8 -*-
import json
import logging
import re
from datetime import datetime

import scrapy
from scrapy.selector import Selector
from scrapy_app.items import CookingStepItem, RecipeItem

logger = logging.getLogger(__name__)


class CookingworkshopSpider(scrapy.Spider):
    name = 'cookingworkshop'
    url = 'http://www.cheftayebeh.ir/feeds/posts/summary?start-index=1&max-results=150&alt=json'

    def start_requests(self):
        yield scrapy.Request(self.url, self.parse)

    def parse(self, response):
        data = self.get_data(response)
        if data is None:
            return
        entries = data['feed']['entry']
        i = 0
        for entry in entries:
            # i += 1    # just uncomment this line for debug
            if i < 2:
                recipe_page = self.get_link(entry['link'], 'self')
                yield scrapy.Request(recipe_page, self.parse_recipe_page)

        next_url = self.get_link(data['feed']['link'], 'next')
        if next_url:
            yield scrapy.Request(next_url, self.parse)

    def get_data(self, response):
        if response.status != 200:
            logger.error("-----Can not retrive page!")
            data = None
        else:
            body = response.body.decode(response.encoding)
            try:
                data = json.loads(body)
            except ValueError:
                logger.error("-----Error in parsing json file")
                data = None
        return data

    def get_link(self, links, rel):
        for link in links:
            if link['rel'] == rel:
                return link['href']
        return None

    def parse_recipe_page(self, response):
        response.selector.remove_namespaces()
        recipe_item = self.parse_recipe_item(response)
        yield recipe_item

        for step in self.parse_steps(response, recipe_item['origin_id']):
            yield step

    def parse_recipe_item(self, response):
        recipe_item = RecipeItem()
        recipe_item['origin_id'] = self.get_id(response.xpath(
            '//entry/id/text()').get())
        recipe_item['published_date'] = response.xpath(
            '//entry/published/text()').get()
        recipe_item['updated_date'] = response.xpath(
            '//entry/updated/text()').get()
        recipe_item['crowled_date'] = datetime.now()
        recipe_item['title_fa'] = response.xpath('//entry/title/text()').get()
        recipe_item['title_en'] = ''
        recipe_item['self_link'] = response.xpath(
            '//link[@rel="self"]/@href').get()
        recipe_item['alternate_link'] = response.xpath(
            '//link[@rel="alternate"]/@href').get()
        recipe_item['author'] = response.xpath('//author/name/text()').get()
        recipe_item['categories'] = response.xpath(
            '//category/@term').getall()
        logger.debug(recipe_item['categories'])

        return recipe_item

    def parse_steps(self, response, recipe_id):
        step_item = CookingStepItem()
        content_txt = response.xpath('//content/text()').get()
        images = self.parse_images(content_txt)
        descriptions = self.parse_descriptions(content_txt)
        for i in range(len(images)):
            yield self.fill_step_item(recipe_id, i+1, images[i], descriptions[i])

    def parse_images(self, content_txt):
        content = Selector(text=content_txt)
        return content.xpath('//img/@src').getall()

    def parse_descriptions(self, content_txt):
        sections = content_txt.split('<img')
        sections.pop(0)  # delete tags before first image tag
        for i in range(len(sections)):
            # modify image tag to convert it to a html tag again
            sections[i] = '<img' + sections[i]
            sections[i] = self.cleanhtml(sections[i])
        return sections

    def cleanhtml(self, raw_html):
        # html tag + enteties like &nsbm
        cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext

    def fill_step_item(self, recipe_id, order, image, description):
        step_item = CookingStepItem()
        step_item['description_fa'] = description
        step_item['description_en'] = ''
        step_item['image'] = image
        step_item['order'] = order
        step_item['recipe'] = recipe_id
        return step_item

    def get_id(self, text):
        tmp = re.search(r'post-(?P<id>\d+)', text)
        return tmp.groupdict().get('id')
