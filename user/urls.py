from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.signup_view, name='signup'),
    path('token-refresh/', views.UserTokenRefreshView.as_view(), name='tokenRefresh'),
]