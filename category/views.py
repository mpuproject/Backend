from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Category
from common.result.result import Result

@require_GET
def get_category_view(request):
    categories = Category.objects.filter(avail="1")

    # 构造返回的数据
    category_list = [
        {
            "id": str(category.category_id),  # UUID 转换为字符串
            "name": category.category_name,
            "avail": category.avail,
        }
        for category in categories
    ]

    result = Result.success_with_data(category_list)
    return JsonResponse(result.to_dict())