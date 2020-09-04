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
    task = scrapyd.schedule(project='default', spider='cookingworkshop')


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value:
            # if value and getattr(value,'url',None):
            image_url = value
            file_name = str(value)
            output.append(
                u'<a href="%s" target="_blank">'
                '<img src="%s" width="100" alt="%s" />'
                '</a>' % (image_url, image_url, file_name)
            )
        output.append(super(AdminFileWidget, self).render(
            name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title_fa', 'title_en']
    search_fields = ['title_fa', 'title_en']


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['title_fa', 'title_en', 'email', 'website']
    search_fields = ['title_fa', 'title_en', 'email', 'website']


class CookingStepInline(admin.TabularInline):
    '''Tabular Inline View for cooking steps of a recipe'''

    model = CookingStep
    min_num = 3
    max_num = 20
    extra = 1
    ordering = ['order']
    fields = ['image',
              'description_fa', 'description_en', ]
    formfield_overrides = {
        models.URLField: {'widget': AdminImageWidget}}

    def get_thumb(self, obj):
        return format_html("<img src='{}'  width='20' height='20' />".format(obj.image))

    get_thumb.allow_tags = True
    get_thumb.__name__ = 'Thumb'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title_fa', 'title_en',
                    'alternate_link', 'published_date', 'author']
    search_fields = ['title_fa', 'title_en',
                     'alternate_link', 'published_date', ]
    actions = [update_recipes]
    inlines = [CookingStepInline, ]
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
    list_display = ['get_thumb', 'description_fa', 'description_en', 'recipe',
                    'order', ]
    search_fields = ['description_fa', 'description_en', 'recipe__title_fa',
                     'order', ]

    def get_thumb(self, obj):
        return format_html("<img src='{}'  width='45' />".format(obj.image))

    get_thumb.allow_tags = True
    get_thumb.__name__ = 'Thumb'


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(CookingStep, CookingStepAdmin)
