from django.urls import path
from . import category_views
from . import subcategory_views

urlpatterns = [
    path('', category_views.get_category_nav_view, name="getCategories"),
    path('all/', category_views.get_category_view, name='getCategoryFilter'),
    path('sub/filter/<str:id>/', subcategory_views.get_subcategory_filter_view, name='getSubcategoryFilter'),
    path('sub/product/', subcategory_views.get_subcategory_products_view, name="getSubcategoryProducts")
]