from django.db import models
from django.contrib.auth.models import AbstractUser
from ecommerce.settings import MEDIA_URL
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sex = models.CharField(max_length=1, blank=False, null=False, default='3')   # "1": man, "2": woman, "3": unknown
    birth = models.DateField(blank=True, null=True)
    email = models.EmailField(unique=True) 
    phone = models.CharField(max_length=14, blank=True, null=True)
    profile_picture = models.CharField(max_length=255, blank=True, null=True, default=MEDIA_URL+'200.png')

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = "用户列表"