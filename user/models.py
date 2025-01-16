from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True) 
    agree_to_privacy_policy = models.BooleanField(default=False)

    def __str__(self):
        return self.username