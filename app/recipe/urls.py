from .views import TagViewSet
from django.urls import path, include

from rest_framework.routers import DefaultRouter

app_name = 'recipe'

router = DefaultRouter()
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls))
]
