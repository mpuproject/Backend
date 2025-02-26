from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.add_comment_view, name='addCommentView'),
    path('list/', views.get_product_comment_view, name='getProductComment'),
    path('get/', views.get_comment_view, name='getComment'),
]