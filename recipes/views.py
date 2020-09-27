from rest_framework import viewsets

from .models import *
from .serializers import *


class RecentPosts (viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all().order_by('published_date')[:9]
    http_method_names = ['get']

    def get_queryset(self):
        return super().get_queryset()
