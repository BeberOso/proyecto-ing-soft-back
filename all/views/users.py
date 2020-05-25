import json

# Django
from django.core.files import File
from django_filters.rest_framework import DjangoFilterBackend

# Django REST Framework
from rest_framework import status, filters, viewsets, mixins
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

# Modelos
from django.contrib.auth.models import User
from all.models import Profile, Rol
from all.serializers import UserSignUpSerializer, UserReadSerializer, UserUpdateSerializer


class UserViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.filter(is_active=True)

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ("username", "first_name")
    search_fields = ("username", "first_name")
    ordering_fields = ("username", "first_name")

    def get_serializer_class(self):
        """Define serializer for API"""
        if self.action == 'list' or self.action == 'retrieve':
            return UserReadSerializer
        elif self.action == 'update_user':
            return UserUpdateSerializer
        else:
            return UserSignUpSerializer

    def get_permissions(self):
        """" Define permisos para este recurso """
        if self.action in ["create", "login"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        if data["password"] != data["confirm_password"]:
            return Response({"detail": "Contraseñas no coinciden."}, status=status.HTTP_400_BAD_REQUEST)
        data.pop("confirm_password")
        usuario = User.objects.create_user(**data)
        rol = Rol.objects.get(nombre="Cliente")
        perfil = Profile.objects.create(user=usuario, user_rol=rol)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=["put"], detail=False)
    def update_user(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        try:
            if user.username != data["username"]:
                try:
                    User.objects.get(username=data["username"])
                    return Response(
                        {"detail": "no se pudo actualizar el usuario"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except User.DoesNotExist:
                    pass
            user.username = data["username"]
            user.first_name = data["first_name"]
            user.last_name = data["last_name"]
            user.email = data["email"]
            perfil, created = Profile.objects.get_or_create(user=user)
            profile = data.get("profile")
            user.save()
            perfil.save()
            serializer = UserReadSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except KeyError as e:
            return Response({"detail": "{} es un campo requerido".format(str(e))}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=False)
    def me(self, request, *args, **kwargs):
        user = request.user
        serializer = UserReadSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def login(self, request, *args, **kwargs):
        data = request.data
        try:
            user = User.objects.get(username=data["username"])
            if user.check_password(data["password"]):
                token, created = Token.objects.get_or_create(user=user)
                serializer = UserReadSerializer(user)
                return Response({"user": serializer.data, "token": token.key}, status=status.HTTP_200_OK)
            return Response({"detail": "Contraseña o Usuario Incorrectos"}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        except KeyError as e:
            return Response({"detail": "{} es un campo requerido".format(str(e))}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["post"], detail=False)
    def logout(self, request, *args, **kwargs):
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response({"detail": "sesión no encontrada"}, status=status.HTTP_404_NOT_FOUND)
