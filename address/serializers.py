from django.utils.html import escape
from rest_framework import serializers
from .models import Address
from django.core.validators import RegexValidator

class AddressSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(max_length=100, 
                                           blank=False, 
                                           null=False,
                                           validators=[
                                               RegexValidator(
                                                   regex='^[a-zA-Z0-9\u4e00-\u9fa5\s\-\.]+$',
                                                   message='Only letters, numbers, Chinese and common symbol are allowed'
                                               ),
                                               lambda value: escape(value)
                                           ])
    phone = serializers.CharField(max_length=20, 
                                  blank=False, 
                                  null=False, 
                                  validators=[lambda value: escape(value)])

    # address info
    province = serializers.CharField(max_length=100,
                                     blank=True,
                                     null=True,)
    city = serializers.CharField(max_length=100,
                                blank=False,
                                null=False,
                                validators=[lambda value: escape(value)])
    district = serializers.CharField(max_length=100, 
                                    blank=False,
                                    null=False,
                                    validators=[lambda value: escape(value)])
    additional_address = serializers.CharField(max_length=255, 
                                               blank=False, 
                                               null=False,
                                               validators=[lambda value: escape(value)])
    postal_code = serializers.CharField(max_length=20,
                                        blank=False,
                                        null=False,
                                        default='000000',
                                        validators=[lambda value: escape(value)])
    
    class Meta:
        model = Address
        fields = '__all__'
    