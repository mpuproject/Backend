from django.db import models
import uuid
from ecommerce.settings import AUTH_USER_MODEL
from address.models import Address

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('0', 'Wechat'),
        ('1', 'AliPay'),
        ('2', 'Bank Z'),
        ('3', 'Bank G'),
        ('4', 'Bank J'),
        ('5', 'Bank N'),
    ]

    TIME_CHOICES = [
        ('0', 'Anytime'),
        ('1', 'Weekday'),
        ('2', 'Weekend'),
    ]

    STATUS_CHOICES = [
        ('0', 'Unpaid'),        #未支付
        ('1', 'Paid'),          #已支付
        ('2', 'Canceled'),      #已取消
    ]

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0', verbose_name='订单状态')
    
    delivery_time = models.CharField(max_length=1, choices=TIME_CHOICES, default='0', verbose_name='配送时间')
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, verbose_name='地址')
    pay_method = models.CharField(max_length=1, choices=PAYMENT_CHOICES, blank=True, null=True, verbose_name='支付方式')

    def __str__(self):
        return f"Order {self.order_id} - {self.user.username}"

    class Meta:
        verbose_name = "订单"
        verbose_name_plural = "订单列表"

class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('0', 'Unpaid'),        #未支付
        ('1', 'Paid'),          #已支付
        ('2', 'Canceled'),      #已取消
        ('3', 'Undelivered'),   #已发货
        ('4', 'Delivered'),     #已送达
        ('5', 'Received'),      #已签收
        ('6', 'Unrefunded'),    #未退款
        ('7', 'Refunded'),      #已退款
        ('8', 'Done'),          #已完成
    ]
# class OrderItem(models.Model):
#     STATUS_CHOICES = [
#         (3, '待发货'),   # Undelivered
#         (4, '已送达'),   # Delivered
#         (5, '已签收'),   # Received
#         (7, '已退款'),   # Refunded
#         (8, '已完成')    # Done
#     ]
    item_id = models.CharField(primary_key=True, max_length=255)
    item_status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='0', verbose_name="订单商品状态")
    product = models.JSONField(default=dict, verbose_name="商品快照")

    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单')

    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return f"OrderItem {self.item_id} - {self.product}"

    class Meta:
        verbose_name = "订单商品"
        verbose_name_plural = "订单商品列表"