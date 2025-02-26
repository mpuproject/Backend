from django.db import models
import uuid
from django.db.models import JSONField
from category.models import Category, SubCategory

class Product(models.Model):
    # 商品状态选项
    STATUS_CHOICES = [
        ('1', 'Available'),  #可用
        ('0', 'Unavailable'),    #不可用
    ]

    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_name = models.CharField(max_length=255, verbose_name="商品名称")
    product_desc = models.TextField(verbose_name="商品描述")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    images = JSONField(default=list, verbose_name="商品图片")
    
    stock_quantity = models.IntegerField(verbose_name="库存数量")
    low_stock_threshold = models.IntegerField(verbose_name="低库存阈值")

    #商品详细信息
    product_details = JSONField(default=list, verbose_name="商品详细信息")
    product_rating = models.FloatField(default=0.0, verbose_name="商品评分")
    rating_num = models.IntegerField(default=0, verbose_name="评论次数")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='0', verbose_name="商品状态")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    # 逻辑删除
    is_deleted = models.BooleanField(default=False)

    #商品分类信息
    sub_category = models.ForeignKey(
        SubCategory,  # 关联到 SubCategory 模型
        on_delete=models.PROTECT,  # 防止删除 SubCategory 时误删商品
        related_name='products',  # 反向查询名称
        verbose_name="商品分类"
    )


    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = "商品"
        verbose_name_plural = "商品列表"