# -*- coding: utf-8 -*-
import scrapy


class RecipeItem(scrapy.Item):
    origin_id = scrapy.Field()
    title_fa = scrapy.Field()
    title_en = scrapy.Field()
    self_link = scrapy.Field()
    alternate_link = scrapy.Field()
    published_date = scrapy.Field()
    updated_date = scrapy.Field()
    crowled_date = scrapy.Field()
    author = scrapy.Field()             # FK
    categories = scrapy.Field()         # FK


class CategoryItem(scrapy.Item):
    title_fa = scrapy.Field()
    title_en = scrapy.Field()


class CookingStepItem(scrapy.Item):
    image = scrapy.Field()
    description_fa = scrapy.Field()
    description_en = scrapy.Field()
    order = scrapy.Field()
    recipe = scrapy.Field()             # FK
