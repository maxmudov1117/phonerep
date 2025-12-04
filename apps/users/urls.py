from django.urls import path
from .views import (
    RegisterView,
    TokenObtainByPhoneView,
    TokenRefreshViewCustom,
    LogoutView,
    ProfileView,
    ChangePasswordView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth-register"),
    path("login/", TokenObtainByPhoneView.as_view(), name="auth-login"),
    path("token/refresh/", TokenRefreshViewCustom.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="auth-logout"),
    path("me/", ProfileView.as_view(), name="auth-me"),
    path("change-password/", ChangePasswordView.as_view(),
         name="auth-change-password"),
]
