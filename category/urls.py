from django.urls import path
from . import category_views
from . import subcategory_views

urlpatterns = [
    path('nav/', category_views.get_category_nav_view, name="getCategoryNav"),
    path('all/', category_views.get_category_view, name='getCategoryFilter'),
    path('sub/filter/<str:id>/', subcategory_views.get_subcategory_filter_view, name='getSubcategoryFilter'),
    path('sub/product/', subcategory_views.get_subcategory_products_view, name="getSubcategoryProducts"),
    path('sub/list/', subcategory_views.get_subcategory_view, name='getSubcategoryList'),
    path('list/', category_views.get_all_categories_view, name='getAllCategories'),
    path('add/', category_views.add_category_view, name='addCategory'),
    path('update/', category_views.update_category_view, name='updateCategory'),
    path('delete/', category_views.delete_category_view, name='deleteCategory'),
    path('admin/list/', category_views.get_admin_all_categories_view, name='adminGetCategories'),
]