""" Modelo Rol"""

# Django
from django.db import models


class Rol(models.Model):
    nombre = models.CharField(max_length=50)
