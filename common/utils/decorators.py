from functools import wraps
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from ..result.result import Result
from datetime import datetime

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
                # 检查 token 是否在有效期内
                now = datetime.now()
                iat = token.payload.get('iat')
                exp = token.payload.get('exp')

                if iat is None or exp is None:
                    raise InvalidToken("Token is missing iat or exp field")

                # 将 iat 和 exp 转换为 datetime 对象
                iat_time = datetime.fromtimestamp(iat)
                exp_time = datetime.fromtimestamp(exp)

                # 检查 token 是否已过期
                if now > exp_time:
                    raise InvalidToken("Token has expired")

                # 检查 token 是否已生效
                if now < iat_time:
                    raise InvalidToken("Token is not yet valid")

                request.user = user  # 将用户对象附加到 request 中
                request.auth = token  # 将新的token附加到request中
            else:
                raise InvalidToken("User login has expired")
        except (InvalidToken, TokenError) as e:
            result = Result.error("Unauthorized: Token is invalid or missing")
            return JsonResponse(result.to_dict(), status=401)

        # 如果验证通过，调用原始视图函数
        return view_func(request, *args, **kwargs)

    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            result = Result.error("No Permission")
            return JsonResponse(result.to_dict(), status=403)
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view

