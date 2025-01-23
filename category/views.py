from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import Category
from common.result.result import Result
import json
from product.models import Product

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
        # 获取分类信息
        category = Category.objects.get(category_id=id)

        # 获取该分类下的二级分类（最多 7 条）
        subcategories = category.subcategories.all()[:7]

        # 构造二级分类数据，并包含对应的商品数据
        subcategory_list = []
        for subcategory in subcategories:
            # 获取当前二级分类下的商品（最多 4 条）
            products = Product.objects.filter(sub_category_id=subcategory.sub_cate_id).order_by('?')[:4]
            product_list = [
                {
                    'id': str(product.product_id),
                    'name': product.product_name,
                    'price': str(product.price),
                    'images': product.images,
                }
                for product in products
            ]

            # 构造当前二级分类的数据，并包含商品列表
            subcategory_data = {
                "id": str(subcategory.sub_cate_id),
                "name": str(subcategory.sub_cate_name),
                "image": str(subcategory.sub_cate_image),
                "products": product_list  # 将商品列表添加到二级分类中
            }
            subcategory_list.append(subcategory_data)

        # 构造返回的数据
        category_data = {
            "id": str(category.category_id),
            "name": str(category.category_name),
            "subcate": subcategory_list  # 包含商品列表的二级分类数据
        }

        result = Result.success_with_data(category_data)
        return JsonResponse(result.to_dict())

    except Category.DoesNotExist:
        result = Result.error("Category not found")
        return JsonResponse(result.to_dict(), status=404)