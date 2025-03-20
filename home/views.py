from django.shortcuts import render
from django.views.decorators.http import require_GET
from product.models import Product
from django.http import JsonResponse
from common.result.result import Result
from common.utils.decorators import token_required
from order.models import Order, OrderItem
from user.models import User
from category.models import Category, SubCategory

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

@require_GET
@token_required
def get_message_count(request):
    try:
        user_id = request.GET.get('userId')
        
        # 获取用户的所有订单ID
        order_ids = Order.objects.filter(user_id=user_id).values_list('order_id', flat=True)
        
        # 获取这些订单的所有OrderItems
        order_items = OrderItem.objects.filter(order_id__in=order_ids)
        
        # 统计不同状态的数量
        unpaid = order_items.filter(item_status='0').count()
        pending = order_items.filter(item_status='1').count()
        review = order_items.filter(item_status='5').count()
        refunding = order_items.filter(item_status='6').count()
        
        # 构造返回数据
        result = Result.success_with_data({
            'unpaid': unpaid,
            'pending': pending,
            'review': review,
            'refunding': refunding
        })
        return JsonResponse(result.to_dict())
        
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict())
        
@require_GET
def get_home_product_view(request):
    try:
        # 获取一个随机的启用状态的子类别
        random_subcategories = SubCategory.objects.filter(status='1').order_by('?')[:2]
        
        if not random_subcategories:
            result = Result.success_with_data([])
            return JsonResponse(result.to_dict())

        category_data = []

        # 获取该子类别下的所有启用状态的商品
        for random_subcategory in random_subcategories:
            products = Product.objects.filter(sub_category=random_subcategory, status='1', is_deleted=False).order_by('?')[:8]

            # 构造返回数据
            category_data.append({
                "id": random_subcategory.category.category_id,
                "name": random_subcategory.category.category_name,
                "saleInfo": random_subcategory.sub_category_name,
                "picture": random_subcategory.image_url if random_subcategory.image_url else "https://picsum.photos/200/600",
                "goods": [
                    {
                        "id": product.product_id,
                        "name": product.product_name,
                        "price": str(product.price),
                        "images": product.images[0]
                    }
                    for product in products
                ]
            })

        # 返回结果
        result = Result.success_with_data(category_data)
        return JsonResponse(result.to_dict())

    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict())
