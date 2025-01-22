from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Category
from common.result.result import Result

@require_GET
def get_categories_view(request):
    categories = Category.objects.filter()

    # 构造返回的数据
    category_list = [
        {
            "id": str(category.category_id),  # UUID 转换为字符串
            "name": category.category_name,
        }
        for category in categories
    ]

    result = Result.success_with_data(category_list)
    return JsonResponse(result.to_dict())

@require_GET
def get_category_view(request, id):
    try:
        category = Category.objects.get(category_id=id)

        subcategories = category.subcategories.all()

        category_data = {
            "id": str(category.category_id),
            "name": str(category.category_name),
            "subcate": [
                {
                    "id": str(subcategory.sub_cate_id),
                    "name": str(subcategory.sub_cate_name),
                    "image": str(subcategory.sub_cate_image)
                } 
                for subcategory in subcategories
            ]
        }
        result = Result.success_with_data(category_data)
        return JsonResponse(result.to_dict())
    
    except Category.DoesNotExist:
        result = Result.error("Category not found")
        return JsonResponse(result.to_dict(), status=404)