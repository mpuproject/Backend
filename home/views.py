from django.shortcuts import render
from django.views.decorators.http import require_GET
from product.models import Product
from django.http import JsonResponse
from common.result.result import Result
import json

@require_GET
def new_view(request):
    # 获取创建时间最近的四个商品
    recent_products = Product.objects.order_by('-created_time')[:4]
    
    # 构造返回的数据
    new_list = []
    for product in recent_products:
        # 获取第一张图片（假设图片存储在 JSON 字段中）
        images = product.images  # 假设 images 是一个 JSON 字段，存储图片 URL 列表
        first_image = images[0] if images else None  # 获取第一张图片，如果没有图片则返回 None
        
        # 构造每个商品的数据
        product_data = {
            'id': str(product.product_id),  # 将 UUID 转换为字符串
            'name': product.product_name,
            'price': str(product.price),  # 将 Decimal 转换为字符串
            'image': first_image,
        }
        new_list.append(product_data)
    
    # 返回 JSON 响应
    result = Result.success_with_data(new_list)
    return JsonResponse(result.to_dict())