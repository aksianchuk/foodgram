from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import CustomUserViewSet


router = SimpleRouter()

router.register('users', CustomUserViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
