from django.shortcuts import render
from rest_framework import generics

from users.models import User
from users.serializers import CustomUserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = CustomUserSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()


class UserListAPIView(generics.ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()