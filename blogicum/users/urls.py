from django.urls import path, reverse_lazy
from django.views.generic import CreateView

from . import views
from .forms import CustomUserCreationForm

app_name = 'users'

urlpatterns = [
    path(
        'registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=CustomUserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path(
        'profile/edit/',
        views.ProfileUpdateView.as_view(),
        name='edit_profile',
    ),
]
