from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_categories_view, name="getCategories"),
    path('<str:id>/', views.get_category_view, name='getCategoryDetail'),
]