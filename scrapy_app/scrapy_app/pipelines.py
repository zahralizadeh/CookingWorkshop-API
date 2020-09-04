# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ObjectDoesNotExist
from recipes.models import Author, Category, CookingStep, Recipe
from scrapy_app.items import CategoryItem, CookingStepItem, RecipeItem

logger = logging.getLogger(__name__)


class RecipesCleanPipeline(object):
    def process_item(self, item, spider):
        for key in item:
            if item[key] is not None:
                if isinstance(item[key], str):
                    item[key] = item[key].replace('ي', 'ی')
                elif isinstance(item[key], list):
                    for i in range(len(item[key])):
                        item[key][i] = item[key][i].replace('ي', 'ی')
        return item


class RecipesPipeline():

    def process_item(self, item, spider):
        # -----------------------------
        # Lets store the items in DB.
        # -----------------------------
        if isinstance(item, CategoryItem):
            return self.process_category(item, spider)
        elif isinstance(item, RecipeItem):
            return self.process_recipe(item, spider)
        elif isinstance(item, CookingStepItem):
            return self.process_cooking_step(item, spider)
        else:
            return item

    def process_category(self, item, spider):
        # ------------------------------------------------------
        # we will use django framework to save our data,
        # so there is no need to fetch & save data manually :)
        # ------------------------------------------------------

        category = Category.objects.filter(
            title_fa=item.get('title_fa'))
        if not category:
            logger.debug("--- Create new `category` instance: %s" %
                         item.get('title_fa'))
            new_category = Category(**item)
            new_category.save()
        else:
            logger.debug('--- Duplicate: category(%s)' % item.get('title_fa'))
            logger.debug(category)
        return item

    def process_recipe(self, item, spider):
        # ------------------------------------------------------
        # we will use django framework to save our data,
        # so there is no need to fetch & save data manually :)
        # ------------------------------------------------------

        recipe = Recipe.objects.filter(
            origin_id=item.get('origin_id'))
        if not recipe:
            logger.debug("--- Create new `recipe` instance: %s" %
                         item.get('title_fa'))
            # get required fields from item to store recipe instance
            data = item
            data['author'] = self.get_author(item.get('author'))
            # categories is a ManyToManyField and we will save it after we saved the item
            categories = self.get_categories(item.get('categories'))

            data.pop('categories', None)
            new_recipe = Recipe(**data)
            new_recipe.save()

            # get the corresponsing list of category objects to update recipe instance
            logger.debug('*** Recipe Category list:')
            logger.debug(categories)
            new_recipe.categories.set(categories)
        else:
            logger.error('--- Duplicate: Recipe(%s)' % item.get('title_fa'))
            logger.error(recipe)
        return item

    def process_cooking_step(self, item, spider):
        # ------------------------------------------------------
        # we will use django framework to save our data,
        # so there is no need to fetch & save data manually :)
        # ------------------------------------------------------
        try:
            recipe = Recipe.objects.get(origin_id=item.get('recipe'))
            data = item
            data['recipe'] = recipe
            new_step = CookingStep(**data)
            new_step.save()

        except ObjectDoesNotExist:
            logger.error('--- Recipe -> %s: Not found!!' %
                         item.get('recipe'))
        return item

    def get_author(self, name):
        try:
            return Author.objects.get(title_en=name)
        except ObjectDoesNotExist:
            logger.error('--- author -> %s: Not found!!' % name)
            return None

    def get_categories(self, categories):
        result = []
        for category in categories:
            try:
                cat_obj = Category.objects.get(title_fa=category)
                result.append(cat_obj)
            except ObjectDoesNotExist:
                logger.error('--- category -> %s: Not found!!' % category)

        return result
