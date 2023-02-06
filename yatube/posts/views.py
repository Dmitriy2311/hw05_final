from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Post, Group, Follow, User
from .utils import paginat


@cache_page(60 * 20)
def index(request):
    """Главная страница."""

    post_list = Post.objects.all()
    page_obj = paginat(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Страница список постов."""

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginat(request, post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Список постов пользователя, общее количество постов,
    инофрмация о пользователе, кнопка подписаться/отписаться."""

    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    page_obj = paginat(request, post_list)
    following = False
    if request.user.is_authenticated and request.user != author:
        if Follow.objects.filter(user=request.user, author=author).exists():
            following = False

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Страница поста и количество постов пользователя."""

    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Добавления поста."""

    form = PostForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user)
        return render(request, 'posts/create_post.html', {'form': form})
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование поста. Доступно только автору."""

    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('posts:post_detail', post.pk)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)

    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Добавление коментариев"""

    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Посты авторов, на которых подписан текущий пользователь."""

    user = get_object_or_404(User, username=request.user)
    followed_people = Follow.objects.filter(user=user).values("author")
    post_list = Post.objects.filter(author__in=followed_people)
    page_obj = paginat(request, post_list)

    context = {
        "page_obj": page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""

    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username)


@login_required
def profile_unfollow(request, username):
    """Отписка от автора."""

    username = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user,
        author__username=username,
    ).delete()
    return redirect("posts:profile", username)
