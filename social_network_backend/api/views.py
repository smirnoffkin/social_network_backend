from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from django.forms.models import model_to_dict

from .models import Friend, Follower, User
from .serializers import (
    GetUserPublicSerializer, 
    GetUserFullInfoSerializer, 
    UserRegistrationSerializer
)
from .services import is_users_friends, is_user_following, is_user_subscribed


class RegistrationAPIView(CreateAPIView):
    """Регистрация нового пользователя"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class GetUserPublicView(RetrieveAPIView):
    """Вывод публичной информации о пользователе"""
    queryset = User.objects.all()
    serializer_class = GetUserPublicSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'username'


class GetUserFullInfoView(RetrieveAPIView):
    """
    Вывод всей информации о пользователе.
    Доступно только для superuser.
    """
    queryset = User.objects.all()
    serializer_class = GetUserFullInfoSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'username'


class ListFriendsView(ListAPIView):
    """Вывод списка всех друзей пользователя"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GetUserPublicSerializer

    def get_queryset(self):
        all_friends = list(Friend.objects.filter(user=self.request.user).all())
        l = False
        if len(all_friends) == 0:
            all_friends = list(Friend.objects.filter(friend=self.request.user).all())
            l = True
        for friend in all_friends:
            friend = model_to_dict(friend)

        if l:
            friends = [User.objects.get(id=friend.user_id) for friend in all_friends]
        else:
            friends = [User.objects.get(id=friend.friend_id) for friend in all_friends]
        return friends


class FriendView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, username):
        """Удалить пользователя из друзей"""
        try:
            user = User.objects.get(username=request.user)
            friend = User.objects.get(username=username)
            friendship = Friend.objects.get(friend=friend.id, user=user.id)
        except (User.DoesNotExist, Friend.DoesNotExist):
            try:
                friendship = Friend.objects.get(friend=user.id, user=friend.id)
            except Friend.DoesNotExist:
                return Response(
                    data="Неверное имя пользователя, либо данный пользователь не ваш друг.", 
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                friendship.delete()
        else:
            friendship.delete()
        return Response(
            data=f"Пользователь {username} был удален из ваших друзей", 
            status=status.HTTP_204_NO_CONTENT
        )


class ListFollowersView(ListAPIView):
    """
    Вывод списка всех подписчиков пользователя.
    (Все входящие запросы).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GetUserPublicSerializer

    def get_queryset(self):
        all_follows = list(Follower.objects.filter(user=self.request.user).all())
        for follow in all_follows:
            follow = model_to_dict(follow)
        return [User.objects.get(id=follow.subscriber_id) for follow in all_follows]


class FollowerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        """Принять запрос дружбы"""
        try:
            user = User.objects.get(username=request.user)
            follower = User.objects.get(username=username)
            follow = Follower.objects.get(user=user.id, subscriber=follower.id)
        except (User.DoesNotExist, Follower.DoesNotExist):
            return Response(
                data="Неверное имя пользователя, либо данный пользователь на вас не подписан, либо он уже ваш друг.", 
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            follow.delete()
            Friend.objects.create(friend=follower, user=user)
        return Response(data=f"Пользователь {username} добавлен в ваши друзья", status=status.HTTP_201_CREATED)

    def delete(self, request, username):
        """Отклонить запрос дружбы"""
        try:
            user = User.objects.get(username=request.user)
            follower = User.objects.get(username=username)
            follow = Follower.objects.get(user=user.id, subscriber=follower.id)
        except (User.DoesNotExist, Follower.DoesNotExist):
            return Response(
                data="Неверное имя пользователя, либо данный пользователь на вас не подписан, либо он уже ваш друг.", 
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            follow.delete()
        return Response(
            data=f"Вы отклонили запрос дружбы от пользователя {username}", 
            status=status.HTTP_204_NO_CONTENT
        )


class ListSubscriptionsView(ListAPIView):
    """
    Вывод списка всех подписок на пользователей.
    (Все исходящие запросы дружбы).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = GetUserPublicSerializer

    def get_queryset(self):
        all_subs = list(Follower.objects.filter(subscriber=self.request.user).all())
        for user_sub in all_subs:
            user_sub = model_to_dict(user_sub)
        return [User.objects.get(id=user_sub.user_id) for user_sub in all_subs]


class SubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, username):
        """Отправить запрос дружбы"""
        try:
            user = User.objects.get(username=request.user)
            possible_friend = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(data="Пользователь не найден", status=status.HTTP_404_NOT_FOUND)
        else:
            if is_users_friends(request.user, username):
                return Response(
                    data=f"Вы уже друзья с пользователем {username}",
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif is_user_following(request.user, username):
                follow = Follower.objects.get(user=user, subscriber=possible_friend)
                follow.delete()
                Friend.objects.create(user=user, friend=possible_friend)
                return Response(
                    data=f"Теперь вы друзья с {username}, так как он был на вас подписан.",
                    status=status.HTTP_201_CREATED
                )
            elif is_user_subscribed(request.user, username):
                return Response(
                    data=f"Вы уже отправили запрос дружбы пользователю {username}", 
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                Follower.objects.create(user=possible_friend, subscriber=user)
        return Response(
            data=f"Запрос дружбы пользователю {username} отправлен", 
            status=status.HTTP_201_CREATED
            )

    def delete(self, request, username):
        """Отменить запрос дружбы"""
        try:
            user = User.objects.get(username=request.user)
            user_follow = User.objects.get(username=username)
            sub = Follower.objects.get(subscriber=user.id, user=user_follow.id)
        except (User.DoesNotExist, Follower.DoesNotExist):
            return Response(
                data=f"Пользователь не найден, либо вы не подписаны на {username}", 
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            sub.delete()
        return Response(
            data=f"Запрос дружбы пользователю {username} отменён", 
            status=status.HTTP_204_NO_CONTENT
        )


class StatusView(APIView):
    """Проверить статус отношений с пользователем"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        if is_users_friends(request.user, username):
            data = f"Пользователь {username} у вас в друзьях."
        elif is_user_following(request.user, username):
            data = f"Пользователь {username} отправил вам запрос дружбы. (Входящая заявка)"
        elif is_user_subscribed(request.user, username):
            data = f"Вы подписаны на пользователя {username}. (Исходящая заявка)"
        else:
            data = f"Вы незнакомы с пользователем {username}."
        return Response(data=data, status=status.HTTP_200_OK)
