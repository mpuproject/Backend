from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from .serializers import CustomTokenRefreshSerializer, CustomTokenObtainPairSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.signup_view, name='signup'),
    path('token-refresh/', CustomTokenRefreshView.as_view(), name='tokenRefresh'),
    path('token/', CustomTokenObtainPairView.as_view(), name='customToken'),
    path('<uuid:id>/', views.update_user_profile, name='updateUser'),
]