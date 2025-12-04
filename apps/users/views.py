from django.shortcuts import render

# Create your views here.
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import (
    RegisterSerializer,
    TokenObtainPairByPhoneSerializer,
    UserSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Register a new user. Returns user detail (no tokens by default).
    """
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class TokenObtainByPhoneView(APIView):
    serializer_class = TokenObtainPairByPhoneSerializer
    """
    Login with phone_number + password, returns access & refresh.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = TokenObtainPairByPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TokenRefreshViewCustom(TokenRefreshView):
    """
    Use simplejwt's TokenRefreshView directly (no change), but import here for urls.
    """
    permission_classes = (permissions.AllowAny,)


class LogoutView(APIView):
    """
    Logout by blacklisting refresh token (client must send refresh token).
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response({"detail": "Token invalid or already blacklisted."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the current user's profile.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated."}, status=status.HTTP_200_OK)
