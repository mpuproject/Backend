from django.urls import path
from . import views
from rest_framework_simplejwt.views import (TokenRefreshView, TokenVerifyView)


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.signup_view, name='signup'),
    path('token-refresh/', TokenRefreshView.as_view(), name='tokenRefresh'),
    path('token-verify/', TokenVerifyView.as_view(), name='tokenVerify'),
]