from django.shortcuts import get_object_or_404
from .models import Question, Answer
from .serializers import QuestionSerializer, AnswerSerializer
from product.models import Product
from common.utils.decorators import token_required
from common.result.result import Result
from django.http import JsonResponse
import logging
from django.views.decorators.http import require_GET, require_POST
import json
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


# 获取问题列表
@require_GET
def get_questions(request, product_id):
    """获取商品问题列表"""
    try:
        logger.info(f"Fetching questions for product: {product_id}")
        product = get_object_or_404(Product, product_id=product_id)
        questions = Question.objects.filter(product=product)
        serializer = QuestionSerializer(questions, many=True)
        return JsonResponse(Result.success_with_data(serializer.data).to_dict())
    except Exception as e:
        logger.error(f"Error fetching questions: {str(e)}")
        return JsonResponse(Result.error("获取问题失败").to_dict(), status=500)

# 添加问题
@require_POST
@token_required
def add_question(request, product_id):
    """添加商品问题"""
    try:
        logger.info(f"Adding question for product: {product_id}")
        product = get_object_or_404(Product, product_id=product_id)
        data = json.loads(request.body)
        
        if not data.get('content'):
            return JsonResponse(Result.error("内容不能为空").to_dict(), status=400)
            
        question = Question.objects.create(
            user=request.user,
            product=product,
            content=strip_tags(data['content'])
        )
        return JsonResponse(Result.success_with_data(
            QuestionSerializer(question).data
        ).to_dict(), status=201)
        
    except Exception as e:
        logger.error(f"Add question error: {str(e)}")
        return JsonResponse(Result.error("添加失败").to_dict(), status=500)

# 回答问题
@require_POST
@token_required
def add_answer(request, question_id):
    """添加问题回答"""
    try:
        logger.info(f"Adding answer for question: {question_id}")
        question = get_object_or_404(Question, question_id=question_id)
        data = json.loads(request.body)
        
        if not data.get('content'):
            return JsonResponse(Result.error("内容不能为空").to_dict(), status=400)
            
        answer = Answer.objects.create(
            user=request.user,
            question=question,
            content=strip_tags(data['content'])
        )
        return JsonResponse(Result.success_with_data(
            AnswerSerializer(answer).data
        ).to_dict(), status=201)
        
    except Exception as e:
        logger.error(f"Add answer error: {str(e)}")
        return JsonResponse(Result.error("回答失败").to_dict(), status=500)
