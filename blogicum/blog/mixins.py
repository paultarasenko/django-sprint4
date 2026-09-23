from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


class PostDetailRedirectMixin:
    """После сохранения/удаления — на страницу публикации."""

    def get_success_url(self):
        return reverse(
            'blog:post_detail', kwargs={'post_id': self.kwargs['post_id']}
        )


class ProfileRedirectMixin:
    """После сохранения/удаления — на страницу профиля автора."""

    def get_success_url(self):
        return reverse(
            'blog:profile', kwargs={'username': self.request.user.username}
        )


class OnlyAuthorMixin(UserPassesTestMixin):
    """Доступ к изменению/удалению объекта — только его автору.

    Используется и для Post, и для Comment: оба набора маршрутов
    содержат в kwargs `post_id`, поэтому неавторизованного или
    авторизованного-но-не-автора пользователя можно единообразно
    отправить на страницу публикации.
    """

    def test_func(self):
        self.object = self.get_object()
        return self.object.author == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            # Стандартное поведение: редирект на страницу входа.
            return super().handle_no_permission()
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
