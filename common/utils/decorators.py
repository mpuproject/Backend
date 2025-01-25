from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from ..result.result import Result

def token_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # 初始化 JWTAuthentication
        authenticator = JWTAuthentication()

        try:
            # 验证 JWT Token
            auth_result = authenticator.authenticate(request)
            if auth_result is not None:
                user, token = auth_result  # 解包用户和 token
                request.user = user  # 将用户对象附加到 request 中
            else:
                raise InvalidToken("User login has expired")
        except (InvalidToken, TokenError) as e:
            result = Result.error("Unauthorized: Token is invalid or missing")
            return JsonResponse(result.to_dict(), status=401)

        # 如果验证通过，调用原始视图函数
        return view_func(request, *args, **kwargs)

    return _wrapped_view

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            result = Result.error("No Permission")
            return JsonResponse(result.to_dict(), status=403)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view