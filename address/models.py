from django.db import models
from django.conf import settings
import uuid

class Address(models.Model):
    address_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # mark of address
    address_tag = models.CharField(max_length=100, blank=False, null=False)

    # related user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')

    # recipient info
    recipient_name = models.CharField(max_length=100, blank=False, null=False)
    phone = models.CharField(max_length=20, blank=False, null=False)

    # address info
    province = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    district = models.CharField(max_length=100, blank=False, null=False)
    additional_address = models.CharField(max_length=255, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=False, null=False, default='000000')
    
    # mark of default
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.recipient_name} - {self.district}, {self.city}, {self.province}, {self.country_code}"

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Address list'