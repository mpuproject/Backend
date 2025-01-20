from django.db import models
import uuid
from ecommerce.settings import AUTH_USER_MODEL
from product.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('0', '未支付'),
        ('1', '已支付'),
        ('2', '已取消'),
        ('3', '待发货'),
        ('4', '已发货'),
        ('5', '已收货'),
        ('6', '退款中'),
        ('7', '已退款'),
        ('8', '已完成'),
    ]

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0', verbose_name="订单状态")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    product_amount = models.IntegerField(verbose_name="商品数量")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="总价")
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    address = models.CharField(blank=False, null=False)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单列表"