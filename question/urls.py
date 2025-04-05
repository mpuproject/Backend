from django.urls import path
from . import views

urlpatterns = [
    path('product/<uuid:product_id>/list/', views.get_questions, name='product_questions'),
    path('product/<uuid:product_id>/add/', views.add_question, name='add_question'),
    path('answer/<uuid:question_id>/add/', views.add_answer, name='answer_question'),
] 