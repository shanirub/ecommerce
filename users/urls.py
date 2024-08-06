from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, profile_view

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', profile_view, name='profile'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
]
