import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=14)
    birthday = models.DateField(blank=True, null=True)


class Friend(models.Model):
    """Модель друга"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friend = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="friends"
    )


class Follower(models.Model):
    """Модель подписчика"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owner'
    )
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )
