from django.urls import path
from . import views

urlpatterns = [
    path('detail/<uuid:pk>/', views.get_details_view, name="getDetails"),
    path('search/', views.SearchView.as_view(), name='search'),
]