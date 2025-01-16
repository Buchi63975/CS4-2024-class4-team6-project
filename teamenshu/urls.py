from django.urls import path
from .views import (
    Home,
    MyPost,
    CreatePost,
    DetailPost,
    UpdatePost,
    DeletePost,
    LikeHome,
    FollowHome,
    FollowDetail,
    FollowList,
    LikeDetail,
    PostDetailView,
)
from teamenshu import views
from django.contrib.auth import views as auth_views
from django.urls import re_path
from teamenshu import consumers

urlpatterns = [
    path("", Home.as_view(), name="home"),
    path("mypost/", MyPost.as_view(), name="mypost"),
    path("create/", CreatePost.as_view(), name="create"),
    path("detail/<int:pk>", DetailPost.as_view(), name="detail"),
    path("detail/<int:pk>/update", UpdatePost.as_view(), name="update"),
    path("detail/<int:pk>/delete", DeletePost.as_view(), name="delete"),
    path("like-home/<int:pk>", LikeHome.as_view(), name="like-home"),
    path("like-detail/<int:pk>", LikeDetail.as_view(), name="like-detail"),
    path("follow-home/<int:pk>", FollowHome.as_view(), name="follow-home"),
    path("follow-detail/<int:pk>", FollowDetail.as_view(), name="follow-detail"),
    path("messages/follow-list/", FollowList.as_view(), name="follow-list"),
    path("messages/mypost/", MyPost.as_view(), name="mypost"),
    path(
        "direct_messages/<str:username>/", views.direct_messages, name="direct_messages"
    ),
    path("inbox/", views.chat_inbox, name="chat_inbox"),
    path("chat/<int:other_user_id>/", views.chat_room, name="chat_room"),
    # API endpoints for direct messages
    # 修正後のURL設定
    path(
        "messages/direct_messages/<str:recipient_username>/",
        views.direct_messages,
        name="direct_messages",
    ),
    path(
        "api/messages/<str:recipient_username>/",
        views.get_messages,
        name="get_messages",
    ),
    path(
        "api/messages/send/<str:recipient_username>/",
        views.send_message,
        name="send_message",
    ),
    # Post detail view and login page
    path("detail/<int:pk>/", PostDetailView.as_view(), name="detail"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="account/login.html"),
        name="login",
    ),
    path("new/", views.new_view, name="new"),
    re_path(r"ws/chat/(?P<username>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
