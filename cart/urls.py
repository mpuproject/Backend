from django.urls import path
from . import views

urlpatterns = [
    path('save/', views.save_cart_view, name="saveCart"),
    path('', views.get_cart_view, name='getCart'),
    path('add/', views.add_cart_view, name='addCart')
]