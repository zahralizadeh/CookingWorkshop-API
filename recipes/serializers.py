from rest_framework import serializers

from .models import Author, Category, CookingStep, Recipe


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['title_fa', 'title_en']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['title_fa', 'title_en']


class CookingStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = CookingStep
        fields = ['order', 'image', 'description_fa', 'description_en']


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=False)
    categories = CategorySerializer(many=True)
    steps = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ['title_fa', 'title_en',
                  'published_date', 'translated', 'author', 'categories', 'steps']

    def get_steps(self, instance):
        steps = instance.steps.all().order_by('order')
        return CookingStepSerializer(steps, many=True).data
