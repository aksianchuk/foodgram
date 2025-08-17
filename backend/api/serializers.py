from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.utils import Base64ImageField


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar'
        ]

    def get_is_subscribed(self, obj):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and request.user.subscriptions.filter(subscribing=obj).exists()
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для аватара пользователя."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ['avatar']
