from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
import json
from common.result.result import Result
from .models import User
from ecommerce.settings import MEDIA_URL

@csrf_exempt  # 禁用 CSRF 验证（仅用于测试，生产环境需要启用）
def login_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                
                access_token = str(refresh.access_token)
                refresh_token = str(refresh) 
                result = Result.success_with_data({
                    "username": user.username,
                    'profile': str(user.profile_picture),
                    "access": access_token,
                    "refresh": refresh_token
                })
                return JsonResponse(result.to_dict())
            else:
                result = Result.error("Incorrect username or password")
                return JsonResponse(result.to_dict(), status=400)
        except json.JSONDecodeError:
            result = Result.error("Invalid request")
            return JsonResponse(result.to_dict(), status=400)
    else:
        result = Result.error("Only POST is supported")
        return JsonResponse(result.to_dict(), status=405)
    
@csrf_exempt
def signup_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            confirm_password = data.get('confirmPwd')

            if not username or not email or not password or not confirm_password:
                result = Result.error('All fields are required')
                return JsonResponse(result.to_dict(), status=400)

            if password != confirm_password:
                result = Result.error('The two passwords do not match')
                return JsonResponse(result.to_dict(), status=400)

            if User.objects.filter(username=username).exists():
                result = Result.error('Username already exists')
                return JsonResponse(result.to_dict(), status=400)

            if User.objects.filter(email=email).exists():
                result = Result.error('Email already exists')
                return JsonResponse(result.to_dict(), status=400)

            # create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                profile_picture=MEDIA_URL+'200.png',
                user_type="0"
            )

            # success
            data = {}
            result = Result.success_with_data({
                'user': {
                    'username': user.username,
                    'email': user.email,
                },
            })
            return JsonResponse(result.to_dict(), status=201)

        except Exception as e:
            result = Result.error(str(e))
            return JsonResponse(result.to_dict(), status=500)

    else:
        result = Result.error('Only POST requests are allowed')
        return JsonResponse(result.to_dict(), status=405)