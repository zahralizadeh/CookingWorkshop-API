from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from scrapyd_api import ScrapydAPI

from .models import Author, Category, CookingStep, Recipe

scrapyd = ScrapydAPI(settings.SCRAPY_ADDRESS)


def update_recipes(modeladmin, request, queryset):
    ''' 
    An action for trigger the scrapy spider for collecting recipes from original site.
    Scrapyd API will manage this process.
    '''
    task = scrapyd.schedule(project='default', spider='cookingworkshop')


class AdminImageURLWidget(AdminFileWidget):
    '''
    This will customize Image widget for showing some thumbnail image preview 
    for each image. This class is a custom class for showing image of each cooking
    step in tabular inline section in each Recipe object.
    As you know I consider image field as URLField, not ImageField, as mention the 
    reason in corresponding model description.
    '''

    def render(self, name, value, attrs=None, renderer=None):
        output = []
        # As a simple URLField is used for keeping image urls, the value
        # contains the url.
        # NOTE: Update the following line when URLField replaced with ImageField:
        # if value and getattr(value,"url", None):
        #   image_url = value.url
        if value:
            image_url = value
            file_name = str(value)
            # NOTE: The width of images can be modified by "image_width"
            image_width = 100
            output.append(
                u'<a href="%s" target="_blank">'
                '<img src="%s" width="%d" alt="%s" />'
                '</a>' % (image_url, image_url, image_width, file_name)
            )
        output.append(super(AdminFileWidget, self).render(
            name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class CategoryAdmin(admin.ModelAdmin):
    '''
    Show categories of post type and food in the admin panel.
    It is a simple table .
    TODO: I may add some inline fprms for related recipes of each category.
    '''
    list_display = ['title_fa', 'title_en']
    search_fields = ['title_fa', 'title_en']


class AuthorAdmin(admin.ModelAdmin):
    '''
    Show Author of different recipes in the admin panel.
    It is a simple table.
    In the meantime I update authors manually, and I have just one author.
    '''
    list_display = ['title_fa', 'title_en', 'email', 'website']
    search_fields = ['title_fa', 'title_en', 'email', 'website']


class CookingStepInline(admin.TabularInline):
    '''
    Tabular Inline View for cooking steps of a recipe.
    Ordering of steps are due the "order" field.
    It will show a image thumbnail of each step using AdminImageWidget class.
    '''

    model = CookingStep
    min_num = 3
    max_num = 20
    extra = 1
    ordering = ['order']
    fields = ['image',
              'description_fa', 'description_en', ]
    formfield_overrides = {
        models.URLField: {'widget': AdminImageURLWidget}}


class RecipeAdmin(admin.ModelAdmin):
    '''
    CRUD panel for maintain Recipes in admin panel. 
    Detailed view of each recipe is consisted of:
    - Main and advanced option by "fieldsets" 
    - Category choose lists by "filter_horizontal"
    - Inline cooking steps by "inlines"
    - Update recipes using trigger the corresponding spider by "actions"
    - Filter the Recipe list by categories using "list_filter"
    NOTE: For update recipes we need at least one Recipe. A fake Recipe can be
    used to trigger the action of update_recipes.
    '''
    list_display = ['title_fa', 'title_en',
                    'alternate_link', 'published_date', 'author']
    search_fields = ['title_fa', 'title_en',
                     'alternate_link', 'published_date', ]
    actions = [update_recipes]
    inlines = [CookingStepInline, ]
    filter_horizontal = ['categories', ]
    list_filter = ['categories', 'author', ]
    fieldsets = (
        (None, {
            'fields': (('title_fa', 'title_en'), ('alternate_link', 'published_date'), 'categories',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('origin_id', 'self_link', 'crowled_date', 'updated_date', 'author', ),
        }),
    )


class CookingStepAdmin(admin.ModelAdmin):
    '''
    CRUD tool for managing cooking steps.
    The thumbnail image of steps displayed in the list
    '''
    list_display = ['get_thumb', 'description_fa', 'description_en', 'recipe',
                    'order', ]
    search_fields = ['description_fa', 'description_en', 'recipe__title_fa',
                     'order', ]

    # NOTE: the width of the thumbnail image can be modified with width attribute
    def get_thumb(self, obj):
        return format_html("<img src='{}'  width='45' />".format(obj.image))

    get_thumb.allow_tags = True
    get_thumb.__name__ = 'Thumb'


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(CookingStep, CookingStepAdmin)
