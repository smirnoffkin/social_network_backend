from django.urls import path

from . import views

urlpatterns = [
    path('user/registration/', views.RegistrationAPIView.as_view()),
    path('user/<slug:username>/', views.GetUserPublicView.as_view()),
    path('user/full_info/<slug:username>/', views.GetUserFullInfoView.as_view()),

    path('profile/<slug:username>/', views.GetUserPublicView.as_view()),

    path('friend/all_friends/', views.ListFriendsView.as_view()),
    path('friend/<slug:username>/', views.FriendView.as_view()),

    path('follow/all_followers/', views.ListFollowersView.as_view()),
    path('follow/my_follower/<slug:username>/', views.FollowerView.as_view()),

    path('subscription/all_subscriptions/', views.ListSubscriptionsView.as_view()),
    path('subscription/subscribe/<slug:username>/', views.SubscriptionView.as_view()),

    path('status/<slug:username>/', views.StatusView.as_view()),
]
