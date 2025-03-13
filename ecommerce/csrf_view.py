from django.middleware.csrf import get_token
from common.result.result import Result
from django.http import JsonResponse
from django.views.decorators.http import require_GET

@require_GET
def get_csrf_token(request):
    csrf_token = get_token(request)
    result = Result.success_with_data({'csrftoken': csrf_token})
    return JsonResponse(result.to_dict())

