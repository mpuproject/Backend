from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
from product.models import Product
from common.utils.decorators import token_required
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from common.result.result import Result
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class QuestionListView(APIView):
    def get(self, request, product_id):
        """获取商品的所有问题"""
        try:
            logger.info(f"Fetching questions for product: {product_id}")
            product = get_object_or_404(Product, product_id=product_id)
            questions = Question.objects.filter(product=product)
            serializer = QuestionSerializer(questions, many=True)
            result = Result.success_with_data(serializer.data)
            return JsonResponse(result.to_dict())
        except Exception as e:
            logger.error(f"Error fetching questions for product {product_id}: {str(e)}")
            result = Result.error(f"获取问题失败: {str(e)}")
            return JsonResponse(result.to_dict(), status=500)

    # 使用DRF的权限类替代装饰器
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, product_id):
        """为商品添加问题"""
        try:
            logger.info(f"Adding question for product: {product_id}")
            product = get_object_or_404(Product, product_id=product_id)
            user = request.user
            content = request.data.get('content')
            
            if not content:
                result = Result.error("问题内容不能为空")
                return JsonResponse(result.to_dict(), status=400)
            
            question = Question.objects.create(
                user=user,
                product=product,
                content=content
            )
            
            serializer = QuestionSerializer(question)
            result = Result.success_with_data(serializer.data)
            return JsonResponse(result.to_dict(), status=201)
        except Exception as e:
            logger.error(f"Error adding question for product {product_id}: {str(e)}")
            result = Result.error(f"添加问题失败: {str(e)}")
            return JsonResponse(result.to_dict(), status=500)

class AnswerView(APIView):
    # 使用DRF的权限类替代装饰器
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, question_id):
        """回答问题"""
        try:
            logger.info(f"Adding answer for question: {question_id}")
            question = get_object_or_404(Question, question_id=question_id)
            user = request.user
            content = request.data.get('content')
            
            if not content:
                result = Result.error("回答内容不能为空")
                return JsonResponse(result.to_dict(), status=400)
            
            answer = Answer.objects.create(
                user=user,
                question=question,
                content=content
            )
            
            serializer = AnswerSerializer(answer)
            result = Result.success_with_data(serializer.data)
            return JsonResponse(result.to_dict(), status=201)
        except Exception as e:
            logger.error(f"Error adding answer for question {question_id}: {str(e)}")
            result = Result.error(f"添加回答失败: {str(e)}")
            return JsonResponse(result.to_dict(), status=500)
