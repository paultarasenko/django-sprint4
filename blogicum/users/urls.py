from django.urls import path, reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm

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
]
