from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import SubCategory
from common.result.result import Result
import json
from product.models import Product
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt


# 获取二级分类导航
@require_GET
def get_subcategory_filter_view(request, id):
    try:
        # 获取二级分类信息
        subCategory = SubCategory.objects.get(sub_cate_id=id)
        
        sub_category_data = {
            "id": subCategory.sub_cate_id,
            "name": subCategory.sub_cate_name,
            "categoryId": subCategory.category.category_id,
            "categoryName": subCategory.category.category_name
        }

        #组装返回数据
        result = Result.success_with_data(sub_category_data)
        return JsonResponse(result.to_dict())

    except SubCategory.DoesNotExist:
        result = Result.error("Sub-category not found")
        return JsonResponse(result.to_dict(), status=404)
    
@csrf_exempt
@require_POST
def get_subcategory_products_view(request):
    try:
        # 解析请求体中的 JSON 数据
        body = json.loads(request.body)
        sub_category_id = body.get('subCategoryId')  # 二级分类 ID
        page = body.get('page', 1)  # 当前页码，默认为 1
        page_size = body.get('pageSize', 20)  # 每页数量，默认为 20
        sort_field = body.get('sortField', 'created_time')  # 排序字段，默认为 created_time

        # 验证二级分类是否存在
        try:
            sub_category = SubCategory.objects.get(sub_cate_id=sub_category_id)
        except SubCategory.DoesNotExist:
            result = Result.error("Subcategory not found")
            return JsonResponse(result.to_dict(), status=404)

        # 获取二级分类下的所有产品，并按指定字段排序
        products = Product.objects.filter(sub_category=sub_category).order_by(sort_field)

        # 分页处理
        paginator = Paginator(products, page_size)

        # 若大于总页数：
        if page > paginator.num_pages:
            response_data = {
                "products": [],
                "pagination": {
                    "current_page": page,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "page_size": page_size
                }
            }
            result = Result.success_with_data(response_data)
            return JsonResponse(result.to_dict())

        page_obj = paginator.get_page(page)

        # 构造返回的数据
        product_list = [
            {
                "id": str(product.product_id),
                "name": product.product_name,
                "price": str(product.price),
                "images": [image for image in product.images if image][:1], #筛选掉空的字符串，并保留第一张
                "created_time": product.created_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            for product in page_obj
        ]

        # 返回分页信息和产品列表
        response_data = {
            "products": product_list,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_size": page_size
            }
        }

        result = Result.success_with_data(response_data)
        return JsonResponse(result.to_dict())

    except json.JSONDecodeError:
        result = Result.error("Invalid JSON format in request body")
        return JsonResponse(result.to_dict(), status=400)