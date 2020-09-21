from django.conf import settings
from django.contrib import admin
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Length
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from scrapyd_api import ScrapydAPI

from .models import Author, Category, CookingStep, Recipe
from .utils import translate_text

scrapyd = ScrapydAPI(settings.SCRAPY_ADDRESS)

# TODO: extract smilies from the ccoking steps


def extract_smilies(modeladmin, request, queryset):
    '''
    Admin Action - Recipe
    Extract cooking steps which have imoji as their image and add description to previous step.
    '''
    for recipe in queryset:
        smilies_steps = recipe.steps.filter(Q(image__icontains='smiles')
                                            | Q(image__icontains='emoticon')
                                            | Q(image__icontains='cheesebuerger.de/')).order_by('-order')
        # print("count is %d" % (smilies_steps.count()))
        for step in smilies_steps:
            # Get previous step
            pre_index = step.order - 1
            if pre_index > 0:
                pre = CookingStep.objects.get(
                    recipe=recipe, order=pre_index)
                # Add description_fa &_en to previous step
                pre.description_fa = pre.description_fa + " " + step.description_fa
                pre.description_en = pre.description_en + " " + step.description_en
                pre.save()
                # Remove the step
                step.delete()

        # Reorder steps
        steps = recipe.steps.all().order_by('order')
        for order, step in enumerate(steps, start=1):
            step.order = order
            step.save()


def update_recipes(modeladmin, request, queryset):
    '''
    Admin Action - Recipe
    An action for trigger the scrapy spider for collecting recipes from original site.
    Scrapyd API will manage this process.
    '''
    task = scrapyd.schedule(project='default', spider='cookingworkshop')


def modify_blank_steps_of_translated_recipes(modeladmin, request, queryset):
    '''
    Admin Action - Recipe
    Modify all translated recipes' cooking steps with no english description
    to a prefabricated description.
    '''
    prefabricated_description = 'A picture is worth a thousand words! :D'
    translated_steps = queryset.select_related().filter(
        recipe__translated=True, description_en='-'
    ).update(description_en=prefabricated_description)


def update_translated_state(modeladmin, request, queryset):
    '''
    Admin Action - Recipe
    Check the Recipe, if the title and all cooking steps are translated,
    then update the translated state to True.
    '''
    # Find translated steps: transalted or empty cooking steps
    ok_steps = CookingStep.objects.filter(
        ~Q(description_en='') | Q(description_fa__in=['', '-']))
    queryset = queryset.prefetch_related('steps').filter(translated=False)
    for item in queryset:
        if set(item.steps.all()).issubset(set(ok_steps)):  # Check if all the steps are translated
            if item.title_en != "":
                item.translated = True
                item.save()


def translate_recipe_title(modeladmin, request, queryset):
    '''
    Admin Action - Recipe
    Translates title of recipes
    '''
    # check if it needs translation or not
    queryset = queryset.filter(title_en__in=['', '-', None])
    # get the translated text and update the item
    for item in queryset:
        item.title_en = translate_text('en', item.title_fa)
        item.save()


def translate_cooking_step(modeladmin, request, queryset):
    '''
    Admin Action - Cooking step
    Translates cooking steps of untranslated cooking steps
    '''
    # check if it needs translation or not
    queryset = queryset.select_related().filter(
        recipe__translated=False, description_en__in=['', '-'])
    # get the translated text and update the item
    for item in queryset:
        item.description_en = translate_text('en', item.description_fa)
        item.save()


class RecipeEnglishTitleAvailableFilter(admin.SimpleListFilter):
    '''
    Admin Filter - Recipe
    Check if the english title is available for recipe or not.
    '''
    title = 'Recipe English Title Available'
    parameter_name = 'title_en'

    def lookups(self, request, model_admin):
        return(
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(~Q(title_en__in=['', None]))

        if self.value() == '0':
            return queryset.filter(title_en__in=['', None])
        return queryset


class IsManuallyTranslatableFilter(admin.SimpleListFilter):
    '''
    Admin Filter - Recipe
    Define a filter for to distinguish recipes which have built-in english description
    with them, so we don't need any google translation for them.
    This recipes have common words including teaspoon, tbsp, tsp, gr, etc in one of
    their cooking steps.
    '''
    title = 'Is Manually Translatable'
    parameter_name = 'manually_translatable'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        ok_steps = CookingStep.objects.filter(
            Q(description_fa__contains='teaspoon')
            |
            Q(description_fa__contains='tsp')
            |
            Q(description_fa__contains='tbsp')
            |
            Q(description_fa__contains='tablespoon')
            |
            Q(description_fa__contains='gr')
            |
            Q(description_fa__contains='cup')
        )
        if self.value() == '1':
            return queryset.filter(steps__in=ok_steps, translated=False)
        if self.value() == '0':
            return queryset.filter(Q(translated=False) & ~Q(steps__in=ok_steps))
        return queryset


class RecipesWithSmiliesFilter(admin.SimpleListFilter):

    title = 'Have smilies in cooking steps'
    parameter_name = 'smilies'

    def lookups(self, request, model_admin):
        return(
            ('1', 'Yes'),
            # ('0', 'No'),
        )

    def queryset(self, request, queryset):
        smilies_steps = CookingStep.objects.filter(
            Q(image__icontains='smiles')
            | Q(image__icontains='emoticon')
            | Q(image__icontains='cheesebuerger.de/')).order_by('-order')
        if self.value() == '1':
            return queryset.prefetch_related('steps').filter(steps__in=smilies_steps).distinct()
        # if self.value() == '0':
        #     return queryset
        return queryset


class IsGoogleTranslatableCookingStepFilter(admin.SimpleListFilter):
    '''
    Admin Filter - Cooking Step
    Check if it is possible to translate the cooking recipe or not.
    '''
    title = 'Is Google Translatable'
    parameter_name = 'translatable'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.select_related('recipe').filter(Q(recipe__translated=False, description_en="") & ~Q(description_fa__in=['', '-']))
        if self.value() == '0':
            return queryset.select_related('recipe').filter(Q(recipe__translated=True) | ~Q(description_en=""))

        return queryset


class EmptyCookingStepFilter(admin.SimpleListFilter):
    '''
    Admin Filter - Cooking Step
    Filter empty cooking steps.
    '''
    title = 'Empty Cooking Step'
    parameter_name = 'empty'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(description_fa__in=['', '-', None])
        elif self.value() == '0':
            return queryset.filter(~Q(description_fa='') & ~Q(description_fa='-'))
        return queryset


class TranslatedCookingStepFilter(admin.SimpleListFilter):
    '''
    Admin Filter - Cooking Step
    Check if the cooking steps are translated or not.
    '''
    title = 'Translated'
    parameter_name = 'translated'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yes'),
            ('0', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(description_en__in=['', None])
        elif self.value() == '1':
            return queryset.filter(~Q(description_en__in=['', None]))
        return queryset


class AdminImageURLWidget(AdminURLFieldWidget):
    '''
    Admin widget - thumbnail image - Recipe
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
        output.append(super(AdminURLFieldWidget, self).render(
            name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class CookingStepInline(admin.TabularInline):
    '''
    Inline view for Recipe
    Tabular Inline View for cooking steps of a recipe.
    Ordering of steps are due the "order" field.
    It will show a image thumbnail of each step using AdminImageWidget class.
    '''

    model = CookingStep
    min_num = 3
    max_num = 20
    extra = 0
    ordering = ['order']
    fields = ['image', 'description_fa', 'description_en', 'order']
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
    list_display = ['title_fa',
                    'title_en',
                    'alternate_link',
                    'published_date',
                    'author',
                    'translated']

    search_fields = ['title_fa',
                     'title_en',
                     'alternate_link',
                     'published_date', ]

    actions = [update_translated_state, translate_recipe_title, update_recipes,
               modify_blank_steps_of_translated_recipes, extract_smilies]

    inlines = [CookingStepInline, ]

    filter_horizontal = ['categories', ]

    list_filter = [RecipeEnglishTitleAvailableFilter, RecipesWithSmiliesFilter,
                   'translated', 'categories', 'author', ]

    fieldsets = (
        (None, {
            'fields': (
                ('title_fa', 'title_en', 'translated'),
                ('alternate_link', 'published_date'),
                'categories',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('origin_id',
                       'self_link',
                       'crowled_date',
                       'updated_date',
                       'author', ),
        }),
    )


class CookingStepAdmin(admin.ModelAdmin):
    '''
    CRUD tool for managing cooking steps.
    The thumbnail image of steps displayed in the list
    in actions dropdown  it is provided to modigy all the "-" english descriptions
    in
    '''
    list_display = ['get_thumb',
                    'description_fa',
                    'description_en',
                    'recipe',
                    'order', ]

    search_fields = ['description_fa',
                     'description_en',
                     'recipe__title_fa',
                     'order', 'image']

    actions = [modify_blank_steps_of_translated_recipes,
               translate_cooking_step, ]

    list_filter = [IsGoogleTranslatableCookingStepFilter,
                   EmptyCookingStepFilter, TranslatedCookingStepFilter]

    # NOTE: the width of the thumbnail image can be modified with width attribute
    def get_thumb(self, obj):
        return format_html("<img src='{}'  width='45' />".format(obj.image))

    get_thumb.allow_tags = True
    get_thumb.__name__ = 'Thumb'


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


admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(CookingStep, CookingStepAdmin)
