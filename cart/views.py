from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from common.result.result import Result
from user.models import User
from .models import Cart
from product.models import Product

@csrf_exempt
@require_POST
def save_cart_view(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user')
        products = data.get('products')

        if not user_id or products is None:
            result = Result.error('Missing user or products')
            return JsonResponse(result.to_dict(), status=400)
        
        cart = Cart.objects.get(user=user_id)
        cart.products = products
        cart.save()

        result = Result.success()
        return JsonResponse(result.to_dict())
    
    except User.DoesNotExist:
        result = Result.error('User not found')
        return JsonResponse(result.to_dict(), status=404)
    
@require_GET
def get_cart_view(request):
    user_id = request.GET.get('id')
    if not user_id:
        result = Result.error("User id missed")
        return JsonResponse(result, status=400)
    
    try:
        cart = Cart.objects.get(user=user_id)
        # 查询商品信息
        products_with_details = []
        for product_info in cart.products:
            product_id = product_info.get('id')
            count = product_info.get('count')
            # 假设商品模型是 Product，字段为 id, price, images
            product = Product.objects.get(product_id=product_id)
            products_with_details.append({
                'id': product_id,
                'name': product.product_name,
                'count': count,
                'price': product.price,  # 获取商品当前价格
                'image': product.images[0] if product.images else None,  # 获取图片列表的第一个值
                'status': not product.is_deleted and product.status == '1' and product.stock_quantity > 0,
            })
        
        cart_data = {
            "id": cart.cart_id,
            "user": cart.user.id,
            "products": products_with_details,  # 替换为包含商品详情的列表
            "created_time": cart.created_time,
            "updated_time": cart.updated_time,
        }
        result = Result.success_with_data(cart_data)
        return JsonResponse(result.to_dict())
    except Cart.DoesNotExist:
        result = Result.error("Cart not found")
        return JsonResponse(result.to_dict(), status=404)
    except Product.DoesNotExist:
        result = Result.error("Product not found")
        return JsonResponse(result.to_dict(), status=404)
    
@csrf_exempt
@require_POST
def add_cart_view(request):
    data = json.loads(request.body)
    user_id = data.get('user_id')

    if not user_id:
        result = Result.error('User ID missed')
        return JsonResponse(result.to_dict(), status=400)


    Cart.objects.create(user_id=user_id)
    
    result = Result.success()
    return JsonResponse(result.to_dict())