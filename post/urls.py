from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, NewsFeedViewset

router = DefaultRouter()
router.register("posts", PostViewSet, "posts")
router.register("newsfeed", NewsFeedViewset, "newsfeed")

urlpatterns = [path('', include(router.urls))]
