from rest_framework import viewsets

from .models import *
from .serializers import *


class RecentPostsViewSet (viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all().order_by('-published_date')[:9]
    http_method_names = ['get']


class AllPostsViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all().order_by('-published_date')
    http_method_names = ['get']
