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

# 获取商品评论详情
@require_GET
def get_product_comment_view(request):
    try:
        product_id = request.GET.get('id')
        filter = request.GET.get('filter')

        comment_list = Comment.objects.filter(product=product_id)

        if filter == 'pic':
            comment_list.filter()

        result = Result.success_with_data()

        return 

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

        comment = Comment.objects.create(
            rating= rating,
            comment_desc=content,
            images= images,
            order_item = order_item,
            product = product
        )

        result=Result.success_with_data({
            'isCommented': True,
            'id': comment.comment_id,
            'commentDesc': comment.comment_desc,
            'rating': comment.rating,
            'orderItemId': comment.order_item.item_id,
            'productId': comment.product.product_id,
            'createdTime': comment.created_time,
        })

        return JsonResponse(result.to_dict())

    except Exception as e:
        result = Result.error(str(e))
        return JsonResponse(result.to_dict(), status=400)