"""
Django settings for ecommerce project.

Generated by 'django-admin startproject' using Django 5.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-x8x^nbv7yy7047lr!!a4stgoyu7ch2myp7^k5&n83r1k7echno"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost']


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'user',
    'product',
    'home',
    'category',
    'cart',
    'image',
    'address',
    'order',
    'comment',
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

from datetime import timedelta
# JWT 配置
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),  # Access Token 有效期
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # Refresh Token 有效期
    'ROTATE_REFRESH_TOKENS': False,                  # 是否在刷新时生成新的 Refresh Token
    'BLACKLIST_AFTER_ROTATION': True,                # 是否将旧的 Refresh Token 加入黑名单
    'UPDATE_LAST_LOGIN': False,                      # 是否更新用户的 last_login 字段

    'ALGORITHM': 'HS256',                            # 加密算法
    'SIGNING_KEY': SECRET_KEY,                       # 签名密钥（默认使用 Django 的 SECRET_KEY）
    'VERIFYING_KEY': None,                           # 验证密钥（用于非对称加密算法，如 RS256）
    'AUDIENCE': None,                                # Token 的目标受众
    'ISSUER': None,                                  # Token 的发行者

    'AUTH_HEADER_TYPES': ('Bearer',),                # 认证头类型
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',        # 认证头的名称
    'USER_ID_FIELD': 'id',                           # 用户标识字段
    'USER_ID_CLAIM': 'user_id',                      # Token 中的用户标识字段
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),  # Token 类型
    'TOKEN_OBTAIN_SERIALIZER': 'user.serializers.CustomTokenObtainPairSerializer',
    'TOKEN_REFRESH_SERIALIZER': 'user.serializers.CustomTokenRefreshSerializer',
}

# reCAPTCHA 配置
RECAPTCHA_SECRET_KEY = '6Lc2P-YqAAAAACHboO5IutjU8IQVQGT7iDfCgMYI'
RECAPTCHA_MIN_SCORE = 0.5  # 设置最低分数

AUTH_USER_MODEL = 'user.User'  # Customized User

import os

MEDIA_URL = '/media/'   # http://localhost:8080/media/
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

CSRF_COOKIE_SAMESITE = 'Lax'  # 允许跨站请求
CSRF_COOKIE_SECURE = False     # 因为使用的是HTTP
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
]

# 启用XSS保护
SECURE_BROWSER_XSS_FILTER = True
# 防止MIME类型嗅探
SECURE_CONTENT_TYPE_NOSNIFF = True
# 禁用iframe嵌入
X_FRAME_OPTIONS = 'DENY'

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]

CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
    'OPTIONS',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

ROOT_URLCONF = "ecommerce.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
