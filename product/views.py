from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from common.result.result import Result
import uuid
from .models import Product

@require_GET
def getDetails_view(request, pk):  # 使用 pk 作为参数名
    try:
        # 使用 pk 查询商品
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        result = Result.error('Product does not exist')
        return JsonResponse(result.to_dict(), status=404)

    # 构造商品数据
    product_data = {
        'id': str(product.product_id),
        'name': product.product_name,
        'price': str(product.price),
        'description': product.product_desc,
        'images': product.images,
        'rating': product.product_rating,
        'stock_quantity': product.stock_quantity,
        'low_stock_threshold': product.low_stock_threshold,
        'details': product.product_details,
    }

    result = Result.success_with_data(product_data)
    return JsonResponse(result.to_dict())