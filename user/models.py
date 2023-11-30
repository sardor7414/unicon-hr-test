from django.db import models
from trello.models import DefaultAbstract
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager

# Create your models here.
class User(AbstractBaseUser, DefaultAbstract, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=13, unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.first_name}, {self.phone}"



