# Django
from django.db import models

# Models
from django.contrib.auth.models import User
from .rol import Rol


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    user_rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name="profiles")

    def __unicode__(self):
        return self.user.username