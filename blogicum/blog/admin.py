from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.db.models import Count

from .models import Category, Comment, Location, Post

User = get_user_model()

admin.site.empty_value_display = 'Не задано'

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class BlogicumUserAdmin(DjangoUserAdmin):
    list_display = DjangoUserAdmin.list_display + ('posts_count',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            posts_count=Count('posts')
        )

    @admin.display(description='Постов', ordering='posts_count')
    def posts_count(self, user):
        return user.posts_count


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'slug')
    search_fields = ('title',)
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published')
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'pub_date', 'author', 'category', 'location', 'is_published'
    )
    search_fields = ('title', 'author__username')
    list_filter = ('category', 'is_published')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'created_at')
