from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order_view, name='createOrder'),
    path('', views.get_order_view, name='getOrderById'),
    
]