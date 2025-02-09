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
@token_required
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
            amount=data.get('amount'),
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

@token_required
@require_GET
def get_order_view(request):
    try:
        id = request.GET.get('id')
        order = Order.objects.get(order_id=id)  # 根据用户 ID 查询订单
        
        # 将订单对象转换为字典列表
        orders_data = {
            'id': order.order_id,
            'deliveryTime': order.delivery_time,
            'products': order.products,
            'orderStatus': order.order_status,
            'amount': order.amount,
        }
        
        result = Result.success_with_data(orders_data)  # 使用转换后的字典列表
        return JsonResponse(result.to_dict())
        
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)
        
@csrf_exempt
@require_http_methods('PUT')
# @token_required
def update_order_view(request):
    try:
        data = json.loads(request.body)
        order_id = data.get('orderId')
        
        # 获取要更新的订单
        order = Order.objects.get(order_id=order_id)
        
        # 更新订单字段
        if 'delivery_time' in data:
            order.delivery_time = data['deliveryTime']
        if 'products' in data:
            order.products = data['products']
        if 'address' in data:
            address_instance = get_object_or_404(Address, address_id=data['address'])
            order.address = address_instance
        if 'order_status' in data:
            order.order_status = data['orderStatus']
        
        order.save()  # 保存更新
        
        # 将更新后的订单对象转换为字典
        order_data = {
            'id': order.order_id,
            'deliveryTime': order.delivery_time,
            'products': order.products,
            'address': order.address.address_id,
            'orderStatus': order.order_status
        }
        
        result = Result.success_with_data(order_data)  # 使用转换后的字典
        return JsonResponse(result.to_dict())
        
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)