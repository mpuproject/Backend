"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from ecommerce import csrf_view
from django.urls import path
from .csrf_view import redirect_to_https


urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include('user.urls')),
    path("product/", include('product.urls')),
    path("home/", include('home.urls')),
    path("category/", include('category.urls')),
    path("cart/", include('cart.urls')),
    path('image/', include('image.urls')),
    path('address/', include('address.urls')),
    path('order/', include('order.urls')),
    path('comment/', include('comment.urls')),
    path('question/', include('question.urls')),
    path('get_csrf/', csrf_view.get_csrf_token),
    path('redirect-to-https/', redirect_to_https, name='redirect_to_https'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
