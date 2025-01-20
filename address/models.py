from django.db import models
from django.conf import settings
import uuid

class Address(models.Model):
    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # mark of address
    address_tag = models.CharField(max_length=100, blank=True, null=True)

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
    
    # mark of default
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recipient_name} - {self.street}, {self.city}, {self.province}, {self.country}"

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Address list'