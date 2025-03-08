from django.http import JsonResponse
from django.contrib.auth import authenticate
import json
from common.result.result import Result
from .models import User
from ecommerce.settings import MEDIA_URL
import uuid
from .serializers import CustomTokenObtainPairSerializer
from django.views.decorators.http import require_POST
from ecommerce import settings
import requests

@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
        
        #检查验证码
        recaptcha_token = data.get('recapchaToken', '')
        verify_recaptcha_view(recaptcha_token, 'login')

        username = data.get('username')
        password = data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            # 使用自定义的序列化器生成token
            serializer = CustomTokenObtainPairSerializer()
            token = serializer.get_token(user)
        
            access_token = str(token.access_token)
            refresh_token = str(token)
            result = Result.success_with_data({
                "id": user.id,
                "username": user.username,
                "profile": str(user.profile_picture),
                "access": access_token,
                "refresh": refresh_token,
            })
            return JsonResponse(result.to_dict())
        else:
            result = Result.error("Incorrect username or password")
            return JsonResponse(result.to_dict(), status=400)
    except json.JSONDecodeError:
        result = Result.error("Invalid request")
        return JsonResponse(result.to_dict(), status=400)
    
@require_POST
def signup_view(request):
    try:
        data = json.loads(request.body)
        
        # 检查验证码
        recaptcha_token = data.get('recaptchToken', '')
        verify_recaptcha_view(recaptcha_token, 'register')

        username = data.get('username')
        email = data.get('email')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        password = data.get('password')
        confirm_password = data.get('confirmPwd')
        is_staff = data.get('is_staff', 0)

        if not username or not email or not first_name or not last_name or not password or not confirm_password:
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
            id=uuid.uuid4(),
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            profile_picture=MEDIA_URL+'200.png',
            is_staff=is_staff,
        )

        # 使用自定义的序列化器生成token
        serializer = CustomTokenObtainPairSerializer()
        token = serializer.get_token(user)
        access_token = str(token.access_token)

        # success
        result = Result.success_with_data({
            'user': {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'access': access_token,
            },
        })
        return JsonResponse(result.to_dict(), status=201)

    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=500)


def verify_recaptcha_view(token, action):
    try:    
        if not token:
            result = Result.error('Token is required')
            return JsonResponse(result.to_dict(), status=400)
        
        # 向 Google 发送验证请求
        verification_data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': token
        }
        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data=verification_data
        )
        res = response.json()
            
        success = res.get('success')
        score = res.get('score', 0)
        verifyAction = res.get('action', '')
        
        if not success or not score < 0.5 or verifyAction != action:
            error_msg = res.get('error-codes', ['reCAPTCHA verification failed'])
            result = Result.error(error_msg)
            return JsonResponse(result.to_dict(), status=400)
        
            
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=500)