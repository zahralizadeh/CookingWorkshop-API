from django.db import models
from django.utils import timezone


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

    def __str__(self):
        if self.title_en is not None and self.title_en != "":
            return self.title_en
        return self.title_fa


class CookingStep(models.Model):
    image = models.URLField(max_length=300, null=True)
    description_fa = models.TextField(null=True)
    description_en = models.TextField(null=True)
    order = models.IntegerField(null=False)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)

    def __str__(self):
        return ("%s - Step %d" % (self.recipe, self.order))
