from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_address_view, name='getAddress'),
    path('add/', views.add_address_view, name='addAddress'),
]