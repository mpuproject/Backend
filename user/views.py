from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.views.decorators.csrf import csrf_exempt
import json
from ecommerce.common.result.result import Result

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
                refresh['username'] = user.username
                result = Result.success_with_data({
                    "access": str(refresh.access_token),
                    "refresh": str(refresh) })
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