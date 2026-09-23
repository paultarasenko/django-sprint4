from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView,
)

from .constants import POSTS_BY_PAGE
from .forms import CommentForm, PostForm
from .mixins import (
    OnlyAuthorMixin, PostDetailRedirectMixin, ProfileRedirectMixin,
)
from .models import Category, Comment, Post

User = get_user_model()


def published_posts(manager=Post.objects):
    """Опубликованные посты: сам пост, его категория и дата публикации."""
    return manager.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def with_comment_count(queryset):
    """Добавить к постам количество комментариев (одним запросом).

    После annotate() с агрегацией по related-полю Django сбрасывает
    неявную сортировку из Post.Meta.ordering, поэтому сортировку нужно
    задать явно.
    """
    return queryset.annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = POSTS_BY_PAGE

    def get_queryset(self):
        return with_comment_count(published_posts())


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = POSTS_BY_PAGE

    def get_category(self):
        if not hasattr(self, '_category'):
            self._category = get_object_or_404(
                Category,
                slug=self.kwargs['category_slug'],
                is_published=True,
            )
        return self._category

    def get_queryset(self):
        return with_comment_count(
            published_posts(self.get_category().posts)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_category()
        return context


class ProfileListView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = POSTS_BY_PAGE

    def get_profile(self):
        if not hasattr(self, '_profile'):
            self._profile = get_object_or_404(
                User, username=self.kwargs['username']
            )
        return self._profile

    def get_queryset(self):
        profile = self.get_profile()
        posts = profile.posts.select_related('category', 'location', 'author')
        if self.request.user != profile:
            posts = published_posts(posts)
        return with_comment_count(posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        return context


def get_visible_post_or_404(request, post_id):
    """Пост, видимый текущему пользователю.

    Себе — всегда, иначе — по правилам показа публикаций.
    """
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        pk=post_id,
    )
    if post.author == request.user:
        return post
    if not published_posts().filter(pk=post.pk).exists():
        raise Http404('Публикация недоступна.')
    return post


def post_detail(request, post_id):
    post = get_visible_post_or_404(request, post_id)
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author'),
    }
    return render(request, 'blog/detail.html', context)


class PostCreateView(LoginRequiredMixin, ProfileRedirectMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(OnlyAuthorMixin, PostDetailRedirectMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class PostDeleteView(OnlyAuthorMixin, ProfileRedirectMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        # Форма нужна только для отображения данных на странице
        # подтверждения удаления — не используем form_class, чтобы
        # она не участвовала в обработке POST-запроса на удаление.
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('blog:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'comments': post.comments.select_related('author'),
    }
    return render(request, 'blog/detail.html', context)


class CommentUpdateView(OnlyAuthorMixin, PostDetailRedirectMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return post.comments.all()


class CommentDeleteView(OnlyAuthorMixin, PostDetailRedirectMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return post.comments.all()
