from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
import json

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
                return JsonResponse({
                    'status': 'success', 
                    'message': 'Login successfully',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh), 
                })
            else:
                return JsonResponse({'status': 'error', 'message': 'Incorrect username or password'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Only POST is supported'}, status=405)