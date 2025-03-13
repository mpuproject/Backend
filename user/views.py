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
from common.utils.decorators import token_required
from django.middleware.csrf import get_token

@require_POST
def login_view(request):
    try:
        data = json.loads(request.body)
        
        #检查验证码
        recaptcha_token = data.get('recaptchaToken', '')
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

            # 刷新 csrf_token
            csrf_token = get_token(request)

            result = Result.success_with_data({
                "id": user.id,
                "username": user.username,
                "profile": str(user.profile_picture),
                "access": access_token,
                "refresh": refresh_token,
            })
            response = JsonResponse(result.to_dict())
            response.set_cookie('csrftoken', csrf_token, path='/')
            return response
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
        recaptcha_token = data.get('recaptchaToken', '')
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

        if len(password) < 6 or len(password) > 20:
            result = Result.error('Password must be 6-20 characters')
            return JsonResponse(result.to_dict(), status=400)
        
        if not check_password_strength(password):
            result = Result.error('Password is too weak')
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
    
@token_required
def update_user_profile(request, id):
    try:
        # 验证用户身份
        user = User.objects.get(id=id)
        if not request.user.is_authenticated or request.user.id != user.id:
            return JsonResponse(Result.error("Unauthorized").to_dict(), status=403)

        data = json.loads(request.body)
        
        # 更新允许修改的字段
        updatable_fields = ['username', 'email', 'phone', 'profile_picture']
        updated = False
        
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
                updated = True
                
        if updated:
            user.save()
            # 刷新token
            serializer = CustomTokenObtainPairSerializer()
            token = serializer.get_token(user)
            access_token = str(token.access_token)
            refresh_token = str(token)

            return JsonResponse(Result.success_with_data({
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "access": access_token,
                "refresh": refresh_token,
                "profile": str(user.profile_picture)
            }).to_dict())
        else:
            return JsonResponse(Result.error("No valid fields to update").to_dict(), status=400)

    except User.DoesNotExist:
        return JsonResponse(Result.error("User not found").to_dict(), status=404)
    except Exception as e:
        return JsonResponse(Result.error(str(e)).to_dict(), status=500)

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
    
def check_password_strength(password):

    conditions = [
        any(c.isupper() for c in password),  # 包含大写字母
        any(c.islower() for c in password),  # 包含小写字母
        any(c.isdigit() for c in password),  # 包含数字
        any(not c.isalnum() for c in password),  # 包含特殊字符
        len(password) >= 8
    ]
    
    # 满足任意4个条件
    return sum(conditions) >= 4
