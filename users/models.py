from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
