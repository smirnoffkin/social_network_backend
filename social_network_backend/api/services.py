from .models import Friend, Follower, User


def is_users_friends(username1: str, username2: str) -> bool:
    """Проверяет, являются ли пользователи друзьями"""
    try:
        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        friendship = Friend.objects.get(user=user1.id, friend=user2.id)
    except (User.DoesNotExist, Friend.DoesNotExist):
        try:
            friendship = Friend.objects.get(user=user2.id, friend=user1.id)
        except Friend.DoesNotExist:
            return False
        else:
            return True
    else:
        return True


def is_user_following(username1: str, username2: str) -> bool:
    """
    Проверка на входящий запрос дружбы.
    Проверяет, является ли user2 подписчиком user1.
    (user2 отправил запрос дружбы user1).
    """
    try:
        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        sub = Follower.objects.get(user=user1.id, subscriber=user2.id)
    except (User.DoesNotExist, Follower.DoesNotExist):
        return False
    else:
        return True


def is_user_subscribed(username1: str, username2: str) -> bool:
    """
    Проверка на исходящий запрос дружбы.
    Проверяет, является ли user1 подписчиком user2.
    (user1 отправил запрос дружбы user2).
    """
    try:
        user1 = User.objects.get(username=username1)
        user2 = User.objects.get(username=username2)
        sub = Follower.objects.get(user=user2.id, subscriber=user1.id)
    except (User.DoesNotExist, Follower.DoesNotExist):
        return False
    else:
        return True
