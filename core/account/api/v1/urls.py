from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from rest_framework.authtoken.views import ObtainAuthToken
from . import views

urlpatterns = [
    # change password
    path(
        "change_password/",
        views.ChangePasswordApiView.as_view(),
        name="change-password",
    ),
    # login token
    path(
        "token/login/",
        ObtainAuthToken.as_view(),
        name="token_login",
    ),
    path(
        "token/logout/",
        views.CustomDiscardAuthToken.as_view(),
        name="token_logout",
    ),
    # login jwt
    path(
        "jwt/create/",
        TokenObtainPairView.as_view(),
        name="token_create",
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
