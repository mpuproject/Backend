from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order_view, name='createOrder'),
    path('', views.get_order_view, name='getOrderById'),
    path('update/', views.update_order_view, name='updateOrder'),
    path('list/', views.get_order_by_user_id_view, name='getOrderByUserId'),
    path('item/update/', views.update_order_item_view, name='updateOrderItem'),
    path('item/get/', views.get_order_item_view, name='getOrderItem'),
    path('admin/list/', views.get_all_orders_view, name='getAllOrders'),
    path('admin/detail/', views.get_order_detail_view, name='get_order_detail'),
    path('admin/item/update/', views.update_admin_item_status_view, name='updateItemStatusView'),
    path('notification/', views.get_order_notification_view, name='getNotificatiion'),
    path('mark-notification/', views.update_order_notification_view, name='updateNotification')
]
