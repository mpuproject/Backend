from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order_view, name='createOrder'),
    path('', views.get_order_view, name='getOrderById'),
    path('update/', views.update_order_view, name='updateOrder'),
    path('list/', views.get_order_by_user_id_view, name='getOrderByUserId'),
    path('item/update/', views.update_order_item_view, name='updateOrderItem'), 
]