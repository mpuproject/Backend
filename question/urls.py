from django.urls import path
from . import views

urlpatterns = [
    path('product/<uuid:product_id>/', views.QuestionListView.as_view(), name='product_questions'),
    path('answer/<uuid:question_id>/', views.AnswerView.as_view(), name='answer_question'),
] 