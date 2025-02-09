from django.shortcuts import render
from django.views.decorators.http import require_GET
from product.models import Product
from django.http import JsonResponse
from common.result.result import Result
import json

# 返回新上架商品
@require_GET
def new_view(request):
    # 获取创建时间最近的四个商品
    recent_products = Product.objects.filter(status='1', is_deleted=False).order_by('-created_time')[:4]
    
    # 构造返回的数据
    new_list = []
    for product in recent_products:
        # 获取第一张图片
        images = product.images  # 假设 images 是一个 JSON 字段，存储图片 URL 列表
        first_image = images[0] if images else None  # 获取第一张图片，如果没有图片则返回 None
        
        # 构造每个商品的数据
        product_data = {
            'id': str(product.product_id),
            'name': product.product_name,
            'price': str(product.price),
            'image': first_image,
        }
        new_list.append(product_data)
    
    # 返回 JSON 响应
    result = Result.success_with_data(new_list)
    return JsonResponse(result.to_dict())

# 返回人气商品
@require_GET
def hot_view(request):
    #评分>=7.5的随机四个商品
    rating_products = Product.objects.filter(status='1', is_deleted=False, product_rating__gte=3.75).order_by('?')[:4]

    # 构造返回数据
    hot_list = []
    for product in rating_products:
        # 获取第一张图片
        images = product.images
        first_image = images[0] if images else None

        product_data = {
            'id': str(product.product_id),
            'name': product.product_name,
            'price': str(product.price),
            'image': first_image,
        }
        hot_list.append(product_data)

    #返回 JSON 响应
    result = Result.success_with_data(hot_list)
    return JsonResponse(result.to_dict())