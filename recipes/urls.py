from django.conf.urls import url
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register('recent_post', views.RecentPosts)

urlpatterns = router.urls
