from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from common.result.result import Result
from user.models import User
from address.models import Address
from common.utils.decorators import token_required
from .models import Order
from django.shortcuts import get_object_or_404

@require_POST
# @token_required
@csrf_exempt
def create_order_view(request):
    try:
        data = json.loads(request.body)
        
        items = data.get('products')
        if not items or items == []:
            result = Result.error("Item list is empty")
            return JsonResponse(result.to_dict(), status=404)
        
        # 获取用户实例
        user_instance = get_object_or_404(User, id=data.get('userId'))
        address_instance = get_object_or_404(Address, address_id=data.get('addressId'))
            
        # 创建订单
        order = Order.objects.create(
            delivery_time=data.get('deliveryTime', '0'),
            products=data.get('products', []),
            user=user_instance,
            address=address_instance,
            order_status='0'  # 默认状态为未支付
        )
        
        # 将订单对象转换为字典
        order_data = {
            'id': order.order_id,
            'delivery_time': order.delivery_time,
            'products': order.products,
            'user': order.user.id,  # 或者其他用户信息
            'address': order.address.address_id,
            'order_status': order.order_status
        }
        
        result = Result.success_with_data(order_data)  # 使用转换后的字典
        return JsonResponse(result.to_dict(), status=201)
        
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)