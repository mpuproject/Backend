from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from common.result.result import Result
from user.models import User
from address.models import Address
from common.utils.decorators import token_required
from .models import Order, OrderItem
from django.shortcuts import get_object_or_404
from product.models import Product
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q

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
            user=user_instance,
            address=address_instance,
            order_status='0'    #默认状态为未支付
        )

        # 创建订单下的商品
        for index, item in enumerate(items):
            OrderItem.objects.create(
                item_status='0',     #默认状态为未支付
                product=item,
                order=order,
                item_id=f"{order.order_id}-{index}"
            )
        
        # 将订单对象转换为字典
        order_data = {
            'id': order.order_id,
            'delivery_time': order.delivery_time,
            'user': order.user.id,
            'address': order.address.address_id,
            'order_status': order.order_status        #默认为未支付
        }
        
        result = Result.success_with_data(order_data)  # 使用转换后的字典
        return JsonResponse(result.to_dict(), status=201)
        
    except Exception as e:
        print("错误信息:", e)
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)

# 根据订单id查询
# @token_required
@require_GET
def get_order_view(request):
    try:
        id = request.GET.get('id')
        order = Order.objects.get(order_id=id)  
        items = OrderItem.objects.filter(order_id=order)
        
        # 计算总金额
        total_amount = sum(item.product['price'] * item.product['count'] for item in items)
        
        # 将订单对象转换为字典
        order_data = {
            'id': order.order_id,
            'deliveryTime': order.delivery_time,
            'products': [{
                'id': item.product['id'],
                'name': item.product['name'],
                'price': item.product['price'],
                'image': item.product['image'],
                'count': item.product['count'],
            } for item in items],
            'orderStatus': order.order_status,
            'amount': total_amount,
            'createdTime': items[0].created_time,
        }
        
        result = Result.success_with_data(order_data)  # 使用转换后的字典列表
        return JsonResponse(result.to_dict())
        
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)
        
# 修改一整个订单
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
        if 'deliveryTime' in data:
            order.delivery_time = data['deliveryTime']
        if 'address' in data:
            address_instance = get_object_or_404(Address, address_id=data['address'])
            order.address = address_instance
        if 'orderStatus' in data:
            order.order_status = data['orderStatus']
                
        
        order.save()  # 保存更新
        
        # 查询与订单关联的所有OrderItem
        order_items = OrderItem.objects.filter(order=order)
        
        if 'orderStatus' in data:
            if data['orderStatus'] == '1' or data['orderStatus'] == '2':
                # 更新所有关联order_items的item_status
                order_items.update(item_status=data['orderStatus'])
        
        # 将更新后的订单对象转换为字典
        order_data = {
            'id': order.order_id,
            'deliveryTime': order.delivery_time,
            'products': [item.product for item in order_items],
            'address': str(order.address.address_id),
            'orderStatus': order.order_status,
        }
        
        result = Result.success_with_data(order_data)  # 使用转换后的字典
        return JsonResponse(result.to_dict())
        
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)
    
# @token_required
@require_GET
def get_order_by_user_id_view(request):
    try:
        user_id = request.GET.get('userId')
        if not user_id:
            return JsonResponse({'code': 400, 'message': 'Missing userId parameter'}, status=400)
            
        status = request.GET.get('itemStatus')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 2))

        # 修改验证列表为字符串格式
        valid_statuses = ['0','1','2','3','4','5','6','7','8','all','undefined']
        if status and status not in valid_statuses:
            return JsonResponse({'code': 400, 'message': 'Invalid status value'}, status=400)

        print(f"接收参数 - userId: {user_id}, itemStatus: {status}, page: {page}, page_size: {page_size}")  # 添加调试日志
        print(f"生成查询条件: {Q(order__user_id=user_id)}")  # 添加调试日志

        # 新过滤逻辑：先找符合条件的订单ID
        if status and status not in ['all', 'undefined']:
            filtered_order_ids = OrderItem.objects.filter(
                Q(order__user_id=user_id) & 
                Q(item_status=status)
            ).values_list('order_id', flat=True).distinct()
            print(f"找到符合条件订单ID: {list(filtered_order_ids)}")  # 添加调试日志
            
            # 获取这些订单的所有商品项
            order_items = OrderItem.objects.filter(
                order_id__in=filtered_order_ids
            ).select_related('order')
        else:
            # 无状态过滤时获取全部
            order_items = OrderItem.objects.filter(
                order__user_id=user_id
            ).select_related('order')

        if not order_items.exists():
            return JsonResponse({
                'code': 200,
                'message': 'success',
                'data': {
                    'count': 0,
                    'results': [],
                    'page': page,
                    'page_size': page_size
                }
            }, status=200)

        # 处理订单分组和排序
        orders_map = {}
        for item in order_items:
            order = item.order
            if order.order_id not in orders_map:
                orders_map[order.order_id] = {
                    'order': order,
                    'items': [],
                    'latest_time': item.created_time
                }
            orders_map[order.order_id]['items'].append(item)
            if item.created_time > orders_map[order.order_id]['latest_time']:
                orders_map[order.order_id]['latest_time'] = item.created_time

        # 按最新时间排序订单
        sorted_orders = sorted(orders_map.values(), key=lambda x: x['latest_time'], reverse=True)

        # 分页处理
        paginator = Paginator(sorted_orders, page_size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            return JsonResponse({'code': 400, 'message': 'Invalid page number'}, status=400)

        # 构建响应数据
        orders_data = []
        for order_group in page_obj:
            order = order_group['order']
            items = order_group['items']
            
            total_amount = sum(item.product['price'] * item.product['count'] for item in items)
            
            status = max(int(item.item_status) for item in items)  # 先转换为数字比较
            status = str(status)  # 再转回字符串保持类型一致
            
            orders_data.append({
                'id': str(order.order_id),
                'created_time': order_group['latest_time'].isoformat(),
                'status': status,
                'total_price': total_amount,
                'post_fee': order.post_fee if hasattr(order, 'post_fee') else 0,
                'items': [{
                    'id': item.item_id,
                    'item_status': item.item_status,
                    'name': item.product.get('name', '未知商品'),
                    'image': item.product.get('image', ''),
                    'created_time': item.created_time.isoformat(),
                    'price': item.product['price'],
                    'quantity': item.product['count']
                } for item in items]
            })

        return JsonResponse({
            'code': 200,
            'message': 'success',
            'data': {
                'count': paginator.count,
                'results': orders_data,
                'page': page,
                'page_size': page_size
            }
        }, status=200)

    except Exception as e:
        import traceback
        traceback.print_exc()  # 打印完整错误堆栈
        return JsonResponse({
            'code': 500,
            'message': f'Server error: {str(e)}',
            'detail': traceback.format_exc()  # 仅在开发环境保留
        }, status=500)