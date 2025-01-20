from django.db import models
import uuid
from django.db.models import JSONField

class Product(models.Model):
    # 商品状态选项
    STATUS_CHOICES = [
        ('ACT', 'Active'),  #可用
        ('INA', 'Inactive'),    #不可用
        ('OOS', 'Out of stock'),    #售罄
    ]

    TAG_CHOICES = [
        ('Living', 'Living'),   #居家
        ('Food', 'Food'),   #美食
        ('Clothes', 'Clothes'), #服饰
        ('Baby', 'Baby'),   #母婴
        ('Health', 'Health'),   #健康
        ('Digital', 'Digital'), #数码
        ('Sports', 'Sports'),    #运动
    ]

    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=255, verbose_name="商品名称")
    product_desc = models.TextField(verbose_name="商品描述")
    product_tag = models.CharField(max_length=100, choices=TAG_CHOICES, verbose_name="分类")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    images = JSONField(default=list, verbose_name="商品图片")
    stock_quantity = models.IntegerField(verbose_name="库存数量")
    low_stock_threshold = models.IntegerField(verbose_name="低库存阈值")

    #商品详细信息
    product_details = JSONField(default=list, verbose_name="商品详细信息")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INA', verbose_name="商品状态")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品列表"
