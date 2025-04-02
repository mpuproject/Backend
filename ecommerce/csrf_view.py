from django.middleware.csrf import get_token
from common.result.result import Result
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def get_csrf_token(request):
    csrf_token = get_token(request)
    result = Result.success_with_data({'csrftoken': csrf_token})
    return JsonResponse(result.to_dict())

# views.py

from django.http import HttpResponsePermanentRedirect

def redirect_to_https(request):
    if not request.is_secure():
        # 获取当前请求的URL
        redirect_url = request.build_absolute_uri()
        # 将URL中的http替换为https
        redirect_url = redirect_url.replace('http://', 'https://')
        # 执行重定向
        return HttpResponsePermanentRedirect(redirect_url)
