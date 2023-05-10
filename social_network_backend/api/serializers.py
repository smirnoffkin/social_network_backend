from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from .models import User, Follower


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор, используемый при регистрации пользователей."""
    class Meta:
        model = User
        fields = (
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'password', 
            'phone', 
            'birthday',
        )
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

    def validate_password(self, value: str) -> str:
        """Хеширование пароля."""
        return make_password(value)


class GetUserPublicSerializer(serializers.ModelSerializer):
    """Вывод публичной информации о пользователе"""
    class Meta:
        model = User
        exclude = (
            "id",
            "email",
            "password",
            "phone",
            "date_joined",
            "birthday",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


class GetUserFullInfoSerializer(serializers.ModelSerializer):
    """
    Вывод всей информации о пользователе.
    Доступно только для superuser.
    """
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "phone",
            "date_joined",
            "birthday",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
            "user_permissions",
        )


class GetListFollowerSerializer(serializers.ModelSerializer):
    """
    Вывод всех пользователей, на которых подписан user.
    (Все исходящие заявки).
    """
    class Meta:
        model = Follower
        fields = (
            "user",
            "subscriber",
        )
