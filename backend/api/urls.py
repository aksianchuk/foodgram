from django.urls import include, path
from rest_framework.routers import SimpleRouter

from api.views import UserViewSet


router = SimpleRouter()

router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
