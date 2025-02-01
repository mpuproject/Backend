from django.urls import path
from . import views

urlpatterns = [
    path('detail/<uuid:pk>/', views.get_details_view, name="getProductByStatus"),
    path('search/', views.SearchView.as_view(), name='search'),
    path('add/', views.add_product_view, name='addProduct'),
    path('delete/<str:id>/', views.delete_product_view, name='deleteProduct'),
    path('update/<str:id>/', views.update_product_view, name='updateProduct'),
    path('list/', views.get_product_view, name='getProduct'),
    path('stock-count/', views.get_product_inventory_status_view, name='getStockCount'),
    path('admin/<uuid:pk>/', views.get_admin_product_view, name='getProduct'),
]