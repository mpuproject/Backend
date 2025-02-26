from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from common.result.result import Result
from django.views.decorators.csrf import csrf_exempt
from common.utils.decorators import token_required
from product.models import Product
from .models import Comment
from order.models import OrderItem
from django.shortcuts import get_object_or_404
from user.models import User
from django.utils import timezone

# 获取商品评论详情
@require_GET
def get_product_comment_view(request):
    try:
        product_id = request.GET.get('productId')
        current_page = int(request.GET.get('currentPage', 1))
        page_size = int(request.GET.get('pageSize', 20))

        # 获取商品评论，按更新时间倒序排列
        comments = Comment.objects.filter(product_id=product_id).order_by('-updated_time')
        
        # 分页处理
        start = (current_page - 1) * page_size
        end = start + page_size
        paginated_comments = comments[start:end]

        # 构建返回数据
        comment_list = []
        for comment in paginated_comments:
            # 通过 order_item 获取 order，再获取用户信息
            user = comment.order_item.order.user
            comment_list.append({
                'id': comment.comment_id,
                'commentDesc': comment.comment_desc,
                'rating': comment.rating,
                'images': comment.images,
                'createdTime': comment.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                'user': {
                    'avatar': user.profile_picture,
                    'username': user.username,
                }
            })

        result = Result.success_with_data({
            'total': comments.count(),
            'currentPage': current_page,
            'pageSize': page_size,
            'comments': comment_list
        })

        return JsonResponse(result.to_dict())

    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)

@require_POST
@token_required
@csrf_exempt
def add_comment_view(request):
    try:
        data = json.loads(request.body)
        item_id = data.get('orderItemId')
        content = data.get('commentDesc', 'User didn\'t say anything.')
        rating = data.get('rating')
        images = data.get('images', [])
        product_id = data.get('productId')

        order_item = get_object_or_404(OrderItem, item_id=item_id)
        product = get_object_or_404(Product, product_id=product_id)

        # 更新商品评分
        new_rating_num = product.rating_num + 1
        new_rating = (product.product_rating * product.rating_num + rating) / new_rating_num
        
        # 更新商品评分和评分数量
        product.product_rating = new_rating
        product.rating_num = new_rating_num
        product.save()

        # 更新订单状态
        order_item.item_status = 8  # 已完成
        order_item.save()

        # 创建新评论
        comment = Comment.objects.create(
            comment_id=item_id,
            rating=rating,
            comment_desc=content,
            images=images,
            order_item=order_item,
            product=product,
            created_time=timezone.now(),
            updated_time=timezone.now(),
        )

        result=Result.success_with_data({
            'isCommented': True,
            'id': comment.comment_id,
            'commentDesc': comment.comment_desc,
            'rating': comment.rating,
            'orderItemId': comment.order_item.item_id,
            'productId': comment.product.product_id,
            'createdTime': comment.created_time,
            'updatedTime': comment.updated_time,
        })

        return JsonResponse(result.to_dict())

    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)
    
@require_GET
def get_comment_view(request):
    try:
        comment_id = request.GET.get('id')

        comment = Comment.objects.get(comment_id=comment_id)

        result = Result.success_with_data({
            'id': comment.comment_id,
            'commentDesc': comment.comment_desc,
            'images': comment.images,
            'updatedTime': comment.updated_time,
            'rating': comment.rating,
            'orderItem': {
                'image': comment.order_item.product["image"],
                'name': comment.order_item.product["name"],
            }
        })
        
        return JsonResponse(result.to_dict())

    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)