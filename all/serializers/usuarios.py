""" Serializer de Usuarios"""

# Django REST Framework
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

# Modelos
from django.contrib.auth.models import User
from all.models import Profile, Rol


class RolReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rol
        fields = "__all__"


class ProfileSerializer(serializers.ModelSerializer):
    user_rol = RolReadSerializer(required=False)

    class Meta:
        model = Profile
        fields = '__all__'


class UserSignUpSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    confirm_password = serializers.CharField(min_length=4)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
            'confirm_password'
        )


class UserUpdateSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'profile',
            'password'
        )


class UserReadSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = (
            "id",
            'username',
            'first_name',
            'last_name',
            'is_superuser',
            'is_staff',
            'email',
            'profile',
        )