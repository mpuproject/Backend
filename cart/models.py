from django.db import models
import uuid
from ecommerce.settings import AUTH_USER_MODEL
from rest_framework import serializers

class Cart(models.Model):
    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False) # 购物车 ID

    # 与用户建立一对一关系
    user = models.OneToOneField(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,  # 如果用户被删除，购物车也会被删除
        related_name='cart',  # 反向查询名称
        verbose_name="用户"
    )

    # 商品信息（JSON 格式）
    products = models.JSONField(default=list, verbose_name="商品列表")

    # 创建时间和更新时间
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"Cart for {self.user.username}"

    class Meta:
        verbose_name = "购物车"
        verbose_name_plural = "购物车列表"