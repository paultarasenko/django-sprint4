from django.contrib.auth import get_user_model
from django.db import models

from .constants import (
    COMMENT_PREVIEW_LENGTH, NAME_MAX_LENGTH, TITLE_MAX_LENGTH,
)

User = get_user_model()


class CreatedAtModel(models.Model):
    """Отметка времени создания — нужна всем записям."""

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class PublishedModel(CreatedAtModel):
    """Отметка времени создания + признак публикации.

    Нужна только тем записям, публикацию которых можно скрыть.
    """

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True


class Category(PublishedModel):
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH, verbose_name='Заголовок'
    )
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы '
            'латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(PublishedModel):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name='Название места'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(PublishedModel):
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH, verbose_name='Заголовок'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и время в будущем — можно '
            'делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор публикации',
        related_name='posts',
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Местоположение', related_name='posts',
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        verbose_name='Категория', related_name='posts',
    )
    image = models.ImageField(
        upload_to='post_images/', blank=True, verbose_name='Изображение',
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Comment(CreatedAtModel):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, verbose_name='Публикация',
        related_name='comments',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор комментария',
        related_name='comments',
    )
    text = models.TextField(verbose_name='Текст комментария')

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)

    def __str__(self):
        return self.text[:COMMENT_PREVIEW_LENGTH]
