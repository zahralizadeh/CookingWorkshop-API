from django.db import models
from django.utils import timezone
from django.utils.safestring import mark_safe


class Author(models.Model):
    title_fa = models.CharField(max_length=250, null=True)
    title_en = models.CharField(max_length=250, null=True)
    website = models.URLField(null=True)
    email = models.EmailField(null=True)
    image = models.URLField(max_length=300, null=True)

    def __str__(self):
        return self.title_en


class Category(models.Model):
    title_fa = models.CharField(max_length=100, null=True)
    title_en = models.CharField(max_length=100, null=True)

    def __str__(self):
        # TODO: regarding to the site language translate the title
        if self.title_en is not None and self.title_en != "":
            return self.title_en
        return self.title_fa


class Recipe (models.Model):
    origin_id = models.CharField(max_length=250, null=True)
    title_fa = models.CharField(max_length=250, null=True)
    title_en = models.CharField(max_length=250, null=True)
    self_link = models.URLField(null=True)
    alternate_link = models.URLField(null=True)
    published_date = models.DateTimeField(null=True)
    updated_date = models.DateTimeField(null=True)
    crowled_date = models.DateTimeField(default=timezone.now())
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category',)
    translated = models.BooleanField(default=False,)

    def __str__(self):
        if self.title_en is not None and self.title_en != "":
            return self.title_en
        elif self.title_fa is not None and self.title_fa != "":
            return self.title_fa
        return self.origin_id


class CookingStep(models.Model):
    '''
    The image field is considered as URLField, not ImageField. because in the
    meantime I can't provide enough space for keeping images and I am using external
    resources as the original site uses.
    '''
    image = models.URLField(max_length=300, null=True)
    description_fa = models.TextField(null=True)
    description_en = models.TextField(null=True, blank=True)
    order = models.IntegerField(null=False)
    recipe = models.ForeignKey(
        'Recipe', related_name='steps', on_delete=models.CASCADE)

    # class Meta:
    #     indexes = [
    #         models.index(fields=[''])
    #     ]

    def __str__(self):
        title = "%s - Step %d" % (self.recipe.title_fa, self.order)
        return title

    def image_show_thumbnail(self):
        return mark_safe(u'<a href="%s" target="_blank">'
                         '<img src="%s" width="%d" alt="%s" />'
                         '</a>' % (image_url, image_url, image_width, file_name))
