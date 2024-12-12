from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.views import View
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from .models import Post, Connection

# Home page displaying posts from users other than the current user
class Home(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        return Post.objects.exclude(user=self.request.user)

# Form for creating a new post
class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'create.html'
    fields = ['title', 'content']
    success_url = reverse_lazy('mypost')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

# Display posts created by the current user
class MyPost(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

# Detailed view of a post
class DetailPost(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'detail.html'

# Edit a post (only accessible to the owner of the post)
class UpdatePost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'update.html'
    fields = ['title', 'content']

    def get_success_url(self, **kwargs):
        return reverse_lazy('detail', kwargs={"pk": self.kwargs["pk"]})

    def test_func(self, **kwargs):
        post = Post.objects.get(pk=self.kwargs["pk"])
        return post.user == self.request.user

# Delete a post (only accessible to the owner of the post)
class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'delete.html'
    success_url = reverse_lazy('mypost')

    def test_func(self, **kwargs):
        post = Post.objects.get(pk=self.kwargs["pk"])
        return post.user == self.request.user

# Base class for handling likes
class LikeBase(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        post = Post.objects.get(pk=self.kwargs['pk'])
        if request.user in post.like.all():
            post.like.remove(request.user)
        else:
            post.like.add(request.user)
        return post

# Like a post from the home page
class LikeHome(LikeBase):
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('home')

# Like a post from the detail page
class LikeDetail(LikeBase):
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('detail', pk=self.kwargs['pk'])

# Base class for handling follow functionality
class FollowBase(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        target_user = Post.objects.get(pk=self.kwargs['pk']).user
        my_connection, _ = Connection.objects.get_or_create(user=request.user)

        if target_user in my_connection.following.all():
            my_connection.following.remove(target_user)
        else:
            my_connection.following.add(target_user)
        return my_connection

# Follow a user from the home page
class FollowHome(FollowBase):
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('home')

# Follow a user from the detail page
class FollowDetail(FollowBase):
    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        return redirect('detail', pk=self.kwargs['pk'])

# Display posts from users followed by the current user
class FollowList(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'list.html'

    def get_queryset(self):
        my_connection, _ = Connection.objects.get_or_create(user=self.request.user)
        return Post.objects.filter(user__in=my_connection.following.all())

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['connection'] = Connection.objects.get_or_create(user=self.request.user)[0]
        return context
