from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from common.result.result import Result
from user.models import User
from address.models import Address
from common.utils.decorators import token_required, admin_required
from .models import Order, OrderItem
from django.shortcuts import get_object_or_404
from product.models import Product
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q, Max
from django.utils import timezone
from comment.models import Comment
from django.db.models import Max

@require_POST
@token_required
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
            # 查询商品并减少库存
            product = get_object_or_404(Product, product_id=item['id'])
            if product.stock_quantity < item['count']:
                raise Exception(f"{product.product_name} is understock")
            product.stock_quantity -= item['count']
            product.save()


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
            'order_status': order.order_status
        }
        result = Result.success_with_data(order_data)
        return JsonResponse(result.to_dict(), status=201)
        
    except Exception as e:
        print("错误信息:", e)
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)

# 根据订单id查询
@require_GET
@token_required
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
                'item_id':item.item_id,
                'item_status': item.item_status,
                'updated_time': item.updated_time,
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
@require_http_methods('PUT')
@token_required
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
                order_items.update(item_status=data['orderStatus'], updated_time=timezone.now())
        
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

@require_http_methods(['PUT'])
@token_required
def update_order_item_view(request):
    try:
        # Add JSON parsing validation
        if not request.body:
            return JsonResponse({'code': 400, 'message': 'Empty request body'}, status=400)
            
        data = json.loads(request.body)
        item_id = data.get('item_id')
        item_status = data.get('item_status')
        print(item_id, item_status)
        if not item_id or not item_status:
            return JsonResponse({
                'code': 400,
                'message': 'Missing required parameters: item_id or item_status'
            }, status=400)
        # 精确查询订单项
        item = get_object_or_404(OrderItem, item_id=item_id)
        item.item_status = item_status
        item.save()

        return JsonResponse({
            'code': 200,
            'data': {
                'item_id': item.item_id,
                'item_status': item_status,
                'updated_time': item.updated_time.isoformat()
            }
        }, status=200)
    except json.JSONDecodeError:
        return JsonResponse({'code': 400, 'message': 'Invalid JSON format'}, status=400)
    except OrderItem.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'message': f'Order item {item_id} not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'message': f'Server error: {str(e)}'
        }, status=500)
        
@require_GET
@token_required
def get_order_by_user_id_view(request):
    try:
        user_id = request.GET.get('userId')
        if not user_id:
            return JsonResponse({'code': 400, 'message': 'Missing userId parameter'}, status=400)
            
        status = request.GET.get('itemStatus')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 5))

        # 修改验证列表为字符串格式
        valid_statuses = ['0','1','2','3','4','5','6','7','8','9','all','undefined']
        if status and status not in valid_statuses:
            return JsonResponse({'code': 400, 'message': 'Invalid status value'}, status=400)

        # 新过滤逻辑：先找符合条件的订单ID
        if status and status not in ['all', 'undefined']:
            filtered_order_ids = OrderItem.objects.filter(
                Q(order__user_id=user_id) & 
                Q(item_status=status)
            ).values_list('order_id', flat=True).distinct()
            
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
                    'updated_time': item.updated_time.isoformat(),
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
        return JsonResponse({
            'code': 500,
            'message': f'Server error: {str(e)}',
        }, status=500)
    
@require_GET
@token_required
def get_order_item_view(request):
    try: 
        item_id = request.GET.get('id')
        if not item_id:
            return JsonResponse({'code': 400, 'message': 'Missing id parameter'}, status=400)
            
        # 获取订单项
        order_item = get_object_or_404(OrderItem, item_id=item_id)
        
        # 检查是否有评论
        is_commented = Comment.objects.filter(order_item=order_item).exists()
        
        # 构建返回数据
        result = Result.success_with_data({
            'orderItemId': order_item.item_id,
            'product': order_item.product,
            'isCommented': is_commented,
        })
        
        return JsonResponse(result.to_dict(), status=200)
        
    except OrderItem.DoesNotExist:
        result = Result.error('Order item not found')
        return JsonResponse(result.to_dict(), status=404)
    except Exception as e:
        result = Result.error(f'Server error: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
        
@require_GET
@token_required
@admin_required
def get_all_orders_view(request):
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        query = request.GET.get('q', '')

        # 通过 OrderItem 的 created_time 进行排序
        orders = Order.objects.exclude(order_status='0').annotate(
            latest_item_time=Max('orderitem__created_time')
        ).order_by('-latest_item_time')

        if query:
            orders = orders.filter(
                Q(order_id__icontains=query) | Q(user__username__icontains=query)
            )
        
        # Apply pagination
        paginator = Paginator(orders, page_size)
        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            return JsonResponse({'code': 400, 'message': 'Invalid page number'}, status=400)

        # Build response data
        orders_data = []
        for order in page_obj:
            # Get items for current order
            items = OrderItem.objects.filter(order=order)
            
            # Calculate total amount
            total_amount = sum(item.product['price'] * item.product['count'] for item in items)
            
            orders_data.append({
                'id': str(order.order_id),
                'createdTime': order.orderitem_set.first().created_time.isoformat(),
                'orderStatus': order.order_status,
                'totalPrice': total_amount,
                'userId': str(order.user.id),
                'username': order.user.username,
                'addressId': str(order.address.address_id),
                'items': [{
                    'id': item.item_id,
                    'itemStatus': item.item_status,
                    'product': item.product,
                    'createdTime': item.created_time.isoformat(),
                    'updatedTime': item.updated_time.isoformat()
                } for item in items]
            })

        result = Result.success_with_data({
            'count': paginator.count,
            'results': orders_data,
            'page': page,
            'pageSize': page_size
        })
        return JsonResponse(result.to_dict(), status=200)

    except Exception as e:
        result = Result.error(f'Server error: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)

@require_http_methods('PUT')
@token_required
@admin_required
def update_admin_item_status_view(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('itemId', '')
        old_status = data.get('oldStatus', '')
        new_status = data.get('newStatus', '')

        if not item_id or not old_status or not new_status:
            result = Result.error('Missing required parameters: itemId, oldStatus or newStatus')
            return JsonResponse(result.to_dict(), status=400)
        
        item = get_object_or_404(OrderItem, item_id=item_id)
        
        if old_status not in ['1', '3', '6', '9']:
            result = Result.error('Error: Item status cannot be changed')
            return JsonResponse(result.to_dict(), status=400)

        if old_status != item.item_status:
            result = Result.error('Item status doesn\'t match')
            return JsonResponse(result.to_dict(), status=400)
        
        if (old_status == '1' and new_status not in ['7', '9']) or (old_status == '9' and new_status != '3') or (old_status == '3' and new_status != '4'):
            result = Result.error('Failed to change item status')
            return JsonResponse(result.to_dict(), status=400)
        
        if old_status == '6' and new_status != '7':
            result = Result.error('Failed to change item status')
            return JsonResponse(result.to_dict(), status=400)
        
        item.item_status = new_status
        item.save()

        result = Result.success()
        return JsonResponse(result.to_dict(), status=200)

    except OrderItem.DoesNotExist:
        result = Result.error(f'Order item {item_id} not found')
        return JsonResponse(result.to_dict(), status=404)
    
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=500)

@require_GET
@token_required
@admin_required
def get_order_detail_view(request):
    try:
        order_id = request.GET.get('id')
        if not order_id:
            return JsonResponse({'code': 400, 'message': 'Missing order ID parameter'}, status=400)

        # 获取订单并预加载地址信息
        order = get_object_or_404(Order, order_id=order_id)
        order_items = OrderItem.objects.filter(order=order)

        # 获取地址信息
        address = order.address
        address_data = {
            'address_id': address.address_id,
            'recipient': address.recipient_name,
            'phone': address.phone,
            'province': address.province,
            'city': address.city,
            'district': address.district,
            'additional_address': address.additional_address,
            'postal_code': address.postal_code
        }

        # 将订单对象转换为字典
        order_data = {
            'id': order.order_id,
            'delivery_time': order.delivery_time,
            'user_id': order.user.id,
            'username': order.user.username,
            'address': address_data,
            'order_status': order.order_status,
            'items': [{
                'id': item.item_id,
                'product': item.product,
                'item_status': item.item_status,
                'quantity': item.product['count'],
                'price': item.product['price'],
                'created_time': item.created_time.isoformat(),
                'updated_time': item.updated_time.isoformat(),
            } for item in order_items]
        }

        result = Result.success_with_data(order_data)
        return JsonResponse(result.to_dict(), status=200)

    except Exception as e:
        return JsonResponse({'code': 500, 'message': f'Server error: {str(e)}'}, status=500)