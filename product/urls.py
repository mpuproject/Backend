from django.urls import path
from . import views

urlpatterns = [
    path('detail/<uuid:pk>/', views.getDetails_view, name="getDetails"),
]