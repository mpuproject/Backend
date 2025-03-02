from django.urls import path
from . import views

urlpatterns = [
    path('new/', views.new_view, name='homeNew'),
    path('hot/', views.hot_view, name='homeHot'),
    path('message/', views.getMessageCount, name='getMessageCount'),
]