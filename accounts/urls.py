from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import BootstrapAuthenticationForm


urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='accounts/login.html',
            authentication_form=BootstrapAuthenticationForm,
        ),
        name='login',
    ),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('password/', views.change_password, name='change_password'),
]
