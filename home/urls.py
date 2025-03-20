from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.new_view, name='homeNew'),
    path('hot/', views.hot_view, name='homeHot'),
    path('message/', views.get_message_count, name='messageCount'),
    path('products/', views.get_home_product_view, name='homeProduct')
]