from django.conf import settings
from django.contrib import admin
from scrapyd_api import ScrapydAPI

from .models import Author, Category, CookingStep, Recipe

scrapyd = ScrapydAPI(settings.SCRAPY_ADDRESS)


def update_recipes(modeladmin, request, queryset):
    task = scrapyd.schedule(project='default', spider='cookingworkshop')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title_fa', 'title_en']
    search_fields = ['title_fa', 'title_en']


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['title_fa', 'title_en', 'email', 'website']
    search_fields = ['title_fa', 'title_en', 'email', 'website']


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title_fa', 'title_en',
                    'alternate_link', 'published_date', 'author']
    search_fields = ['title_fa', 'title_en',
                     'alternate_link', 'published_date', ]
    actions = [update_recipes]


class CookingStepAdmin(admin.ModelAdmin):
    list_display = ['description_fa', 'description_en', 'recipe',
                    'order', ]
    search_fields = ['description_fa', 'description_en', 'recipe__title_fa',
                     'order', ]


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(CookingStep, CookingStepAdmin)
