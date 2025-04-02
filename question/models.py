from django.db import models
import uuid
from user.models import User
from product.models import Product

class Question(models.Model):
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    content = models.TextField(verbose_name="问题内容")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="提问时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"{self.user.username}'s question: {self.content[:30]}"
    
    class Meta:
        verbose_name = "商品问题"
        verbose_name_plural = "商品问题列表"
        ordering = ['-created_time']

class Answer(models.Model):
    answer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField(verbose_name="回答内容")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="回答时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    def __str__(self):
        return f"{self.user.username}'s answer: {self.content[:30]}"
    
    class Meta:
        verbose_name = "问题回答"
        verbose_name_plural = "问题回答列表"
        ordering = ['-created_time']
