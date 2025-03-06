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

        if not item_id or not rating or not product_id:
            result = Result.error("Missing parameters: orderItemId / rating / productId")
            return JsonResponse(result.to_dict(), status=400)

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
    
@require_http_methods('DELETE')
@token_required
@csrf_exempt
def delete_comment_view(request):
    try:
        data = json.loads(request.body)
        id = data.get('id')
        
        # 获取要删除的评论
        comment = get_object_or_404(Comment, comment_id=id)
        product = comment.product
        
        # 重新计算商品评分
        if product.rating_num > 1:
            new_rating_num = product.rating_num - 1
            new_rating = (product.product_rating * product.rating_num - comment.rating) / new_rating_num
            product.product_rating = new_rating
            product.rating_num = new_rating_num
        else:
            # 如果这是最后一个评论，重置评分
            product.product_rating = 0
            product.rating_num = 0
        
        # 保存更新后的商品评分
        product.save()
        
        # 删除评论
        comment.delete()
        
        result = Result.success()
        return JsonResponse(result.to_dict())

    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)

@require_http_methods('PUT')
@token_required
@csrf_exempt
def update_comment_view(request):
    try:
        data = json.loads(request.body)
        comment_id = data.get('id')
        new_rating = data.get('rating')
        new_content = data.get('commentDesc', 'User didn\'t say anything.')
        new_images = data.get('images', [])
        
        # 获取要更新的评论
        comment = get_object_or_404(Comment, comment_id=comment_id)
        product = comment.product
        
        # 先恢复原评分
        if product.rating_num > 0:
            old_rating = comment.rating
            total_rating = product.product_rating * product.rating_num - old_rating
            
            # 更新新评分
            total_rating += new_rating
            product.product_rating = total_rating / product.rating_num
            product.save()
        
        # 更新评论内容
        comment.rating = new_rating
        comment.comment_desc = new_content
        comment.images = new_images
        comment.updated_time = timezone.now()
        comment.save()
        
        result = Result.success_with_data({
            'id': comment.comment_id,
            'commentDesc': comment.comment_desc,
            'rating': comment.rating,
            'images': comment.images,
            'updatedTime': comment.updated_time
        })
        return JsonResponse(result.to_dict())
        
    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)
        