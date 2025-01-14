from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Follow, Message
from .forms import MessageForm
from .models import Post, Connection
import logging
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .models import DirectMessage
from django.db import models


class Home(LoginRequiredMixin, ListView):
    """HOMEページで、自分以外のユーザー投稿をリスト表示"""

    model = Post
    template_name = "list.html"

    def get_queryset(self):
        """リクエストユーザーのみ除外"""
        return Post.objects.exclude(user=self.request.user)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        # get_or_createにしないとサインアップ時オブジェクトがないためエラーになる
        context["connection"] = Connection.objects.get_or_create(user=self.request.user)
        return context


class MyPost(LoginRequiredMixin, ListView):
    """自分の投稿のみ表示"""

    model = Post
    template_name = "list.html"

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)


class CreatePost(LoginRequiredMixin, CreateView):
    """投稿フォーム"""

    model = Post
    template_name = "create.html"
    fields = ["title", "content"]
    success_url = reverse_lazy("mypost")

    def form_valid(self, form):
        """投稿ユーザーをリクエストユーザーと紐付け"""
        form.instance.user = self.request.user
        return super().form_valid(form)


class DetailPost(LoginRequiredMixin, DetailView):
    """投稿詳細ページ"""

    model = Post
    template_name = "detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["connection"] = Connection.objects.get_or_create(user=self.request.user)
        return context


class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """投稿編集ページ"""

    model = Post
    template_name = "update.html"
    fields = ["title", "content"]

    def get_success_url(self, **kwargs):
        """編集完了後の遷移先"""
        pk = self.kwargs["pk"]
        return reverse_lazy("detail", kwargs={"pk": pk})

    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return post.user == self.request.user


class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """投稿編集ページ"""

    model = Post
    template_name = "delete.html"
    success_url = reverse_lazy("mypost")

    def test_func(self, **kwargs):
        """アクセスできるユーザーを制限"""
        pk = self.kwargs["pk"]
        post = Post.objects.get(pk=pk)
        return post.user == self.request.user


###############################################################
# いいね処理
class LikeBase(LoginRequiredMixin, View):
    """いいねのベース。リダイレクト先を以降で継承先で設定"""

    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        related_post = Post.objects.get(pk=pk)

        if self.request.user in related_post.like.all():
            obj = related_post.like.remove(self.request.user)
        else:
            obj = related_post.like.add(self.request.user)
        return obj


class LikeHome(LikeBase):
    """HOMEページでいいねした場合"""

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect("home")


class LikeDetail(LikeBase):
    """詳細ページでいいねした場合"""

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        pk = self.kwargs["pk"]
        return redirect("detail", pk)


###############################################################


###############################################################
# フォロー処理
class FollowBase(LoginRequiredMixin, View):
    """フォローのベース。リダイレクト先を以降で継承先で設定"""

    def get(self, request, *args, **kwargs):
        pk = self.kwargs["pk"]
        target_user = Post.objects.get(pk=pk).user

        my_connection = Connection.objects.get_or_create(user=self.request.user)

        if target_user in my_connection[0].following.all():
            obj = my_connection[0].following.remove(target_user)
        else:
            obj = my_connection[0].following.add(target_user)
        return obj


class FollowHome(FollowBase):
    """HOMEページでフォローした場合"""

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect("home")


class FollowDetail(FollowBase):
    """詳細ページでフォローした場合"""

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        pk = self.kwargs["pk"]
        return redirect("detail", pk)


###############################################################


class FollowList(LoginRequiredMixin, ListView):
    """フォローしたユーザーの投稿をリスト表示"""

    model = Post
    template_name = "list.html"

    def get_queryset(self):
        """フォローリスト内にユーザーが含まれている場合のみクエリセット返す"""
        my_connection = Connection.objects.get_or_create(user=self.request.user)
        all_follow = my_connection[0].following.all()
        return Post.objects.filter(user__in=all_follow)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["connection"] = Connection.objects.get_or_create(user=self.request.user)
        return context


logger = logging.getLogger(__name__)


@login_required
def chat_inbox(request):
    # Get unique conversations for the current user
    conversations = (
        Message.objects.filter(Q(sender=request.user) | Q(receiver=request.user))
        .values("sender", "receiver")
        .distinct()
    )

    # Get the latest message for each conversation
    chat_list = []
    for conv in conversations:
        other_user = (
            conv["receiver"] if conv["sender"] == request.user.id else conv["sender"]
        )
        latest_message = Message.objects.filter(
            Q(sender=request.user, receiver=other_user)
            | Q(sender=other_user, receiver=request.user)
        ).latest("timestamp")

        chat_list.append({"other_user": other_user, "latest_message": latest_message})

    return render(request, "chat/inbox.html", {"chat_list": chat_list})


@login_required
def chat_room(request, other_user_id):
    messages = Message.objects.filter(
        Q(sender=request.user, receiver_id=other_user_id)
        | Q(sender_id=other_user_id, receiver=request.user)
    ).order_by("timestamp")

    # Mark messages as read
    Message.objects.filter(
        sender_id=other_user_id, receiver=request.user, is_read=False
    ).update(is_read=True)

    return render(
        request,
        "chat/room.html",
        {"messages": messages, "other_user_id": other_user_id},
    )


@login_required
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        receiver_id = data.get("receiver_id")
        content = data.get("content")

        message = DirectMessage.objects.create(
            sender=request.user,
            recipient_id=receiver_id,  # 'recipient'に変更
            message=content,
        )

        return JsonResponse(
            {
                "status": "success",
                "message": {
                    "id": message.id,
                    "content": message.content,
                    "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "sender": message.sender.username,
                },
            }
        )
    return JsonResponse({"status": "error"}, status=400)


def index(request):
    return render(request, "index.html")


@login_required
def direct_messages(request, username):
    recipient = get_object_or_404(get_user_model(), username=username)

    # 自分自身へのDMは許可
    if request.user.username == username:
        return render(
            request,
            "dm.html",
            {"recipient_username": username, "recipient": recipient},
        )

    # フォロー関係のチェック
    my_connection = Connection.objects.get_or_create(user=request.user)[0]
    if recipient not in my_connection.following.all():
        messages.warning(request, "フォローしているユーザーのみDMを送信できます")
        return redirect("home")

    return render(
        request,
        "dm.html",
        {"recipient_username": username, "recipient": recipient},
    )


@login_required
@csrf_exempt
def get_messages(request, username):
    if request.method == "GET":
        # メッセージの取得
        messages_list = DirectMessage.objects.filter(
            (
                Q(sender=request.user, recipient__username=username)
                | Q(sender__username=username, recipient=request.user)
            )
        ).order_by("created_at")

        logger.debug(f"Messages for {username}: {messages_list}")

        return JsonResponse(
            [
                {
                    "id": msg.id,
                    "message": msg.message,
                    "from": msg.sender.username,
                    "timestamp": msg.created_at.isoformat(),
                }
                for msg in messages_list
            ],
            safe=False,
        )

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            message_content = data.get("message", "").strip()
            if not message_content:
                return JsonResponse(
                    {"error": "メッセージを入力してください"}, status=400
                )

            # フォロー関係のチェック
            recipient = get_object_or_404(get_user_model(), username=username)
            my_connection = Connection.objects.get_or_create(user=request.user)[0]
            followed_users = my_connection.following.all()

            # ログを追加して、送信先がフォロー関係にあるか確認
            logger.debug(
                f"User {request.user.username} is following: {[user.username for user in followed_users]}"
            )

            if recipient not in followed_users:
                return JsonResponse(
                    {"error": "フォローしているユーザーのみDMを送信できます"},
                    status=403,
                )

            # メッセージの作成
            message = DirectMessage.objects.create(
                sender=request.user,
                recipient=recipient,
                message=message_content,
                is_read=False,  # 明示的にis_readを設定
            )

            return JsonResponse(
                {
                    "id": message.id,
                    "message": message.message,
                    "from": message.sender.username,
                    "timestamp": message.created_at.isoformat(),
                }
            )
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return JsonResponse({"error": "サーバーエラーが発生しました"}, status=500)

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Post, Comment
from .forms import CommentForm

class PostDetailView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        comments = post.comments.filter(parent__isnull=True)
        comment_form = CommentForm()
        return render(request, 'detail.html', {
            'object': post,
            'comments': comments,
            'comment_form': comment_form,
        })

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            parent = Comment.objects.filter(id=parent_id).first() if parent_id else None
            Comment.objects.create(
                post=post,
                user=request.user,
                content=form.cleaned_data['content'],
                parent=parent,
            )
        return redirect('detail', pk=pk)
