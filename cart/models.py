from django.db import models
import uuid
from ecommerce.settings import AUTH_USER_MODEL
from product.models import Product

class Cart(models.Model):
    cart_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # 通过中间模型 CartItem 关联 Product
    products = models.ManyToManyField(Product, through='CartItem', verbose_name="商品")

    def __str__(self):
        return f"Cart {self.cart_id} - {self.user.username}"

    class Meta:
        verbose_name = "购物车"
        verbose_name_plural = "购物车列表"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="购物车")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="商品")
    quantity = models.IntegerField(default=1, verbose_name="数量")

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name} in Cart {self.cart.cart_id}"

    class Meta:
        verbose_name = "购物车商品"
        verbose_name_plural = "购物车商品"