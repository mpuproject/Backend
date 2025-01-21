from django.db import models
import uuid

class Category(models.Model):
    category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category_name = models.CharField(max_length=100, null=False, blank=False)
    avail = models.CharField(max_length=1, blank=False, null=False, default='1') # "0"-禁用，"1"-启用

    def __str__(self):
        return self.category_name

class SubCategory(models.Model):
    sub_cate_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_cate_name = models.CharField(max_length=100, blank=False, null=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='subcategories')

    def __str__(self):
        return self.sub_cate_name