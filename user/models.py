from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from ecommerce.settings import MEDIA_ROOT

class User(AbstractUser):
    sex = models.CharField(max_length=1, blank=False, null=False, default='3')   # "1": man, "2": woman, "3": unknown
    birth = models.DateField(blank=True, null=True)
    email = models.EmailField(unique=True) 
    phone = models.CharField(max_length=14, blank=True, null=True)
    profile_picture = models.ImageField(upload_to=MEDIA_ROOT, blank=True, null=True, default=MEDIA_ROOT+'200.png')

    def __str__(self):
        return self.username
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = "User list"
    
class Address(models.Model):
    # related user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')

    # recipient info
    recipient_name = models.CharField(max_length=100, blank=False, null=False)
    phone = models.CharField(max_length=14, blank=False, null=False)

    # address info
    country = models.CharField(max_length=50, blank=False, null=False)
    province = models.CharField(max_length=50, blank=False, null=False)
    city = models.CharField(max_length=50, blank=False, null=False)
    district = models.CharField(max_length=50, blank=False, null=False)
    detailed = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20, blank=False, null=False)

    # mark of address
    address_type = models.CharField(max_length=50, blank=True, null=True)
    
    # mark of default
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recipient_name} - {self.street}, {self.city}, {self.province}, {self.country}"

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Address list'