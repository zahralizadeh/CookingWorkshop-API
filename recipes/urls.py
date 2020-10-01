from django.conf.urls import url
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('recent_posts', views.RecentPostsViewSet)
router.register('all_posts', views.AllPostsViewSet)

urlpatterns = router.urls
