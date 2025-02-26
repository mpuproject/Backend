from django.db import models
import uuid
from product.models import Product
from order.models import OrderItem

class Comment(models.Model):
    comment_id = models.CharField(primary_key=True, max_length=255, editable=False)
    rating = models.FloatField(default=0.0, verbose_name="评价评分")
    comment_desc = models.TextField(default='The user didn\'t say anything', verbose_name="评价描述")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    images = models.JSONField(default=list, verbose_name='评论图片')

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='产品'
    )

    order_item = models.OneToOneField(
        OrderItem,
        on_delete=models.CASCADE,
        related_name='comment',
        verbose_name='小订单',
    )

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论列表"