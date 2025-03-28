from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import Category
from common.result.result import Result
import json
from product.models import Product
from django.db.models import Q
import uuid
from common.utils.decorators import token_required, admin_required
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__) 
# 获取所有分类目录
@require_GET
def get_category_nav_view(request):
    #截取7条可用记录
    categories = Category.objects.filter(status="1")[:7]

    # 构造返回的数据
    category_list = [
        {
            "id": str(category.category_id),  # UUID 转换为字符串
            "name": category.category_name,
        }
        for category in categories
    ]

    result = Result.success_with_data(category_list)
    return JsonResponse(result.to_dict())

@require_POST
def get_category_view(request):
    try:
        id = json.loads(request.body).get("id")

        # 获取分类信息
        category = Category.objects.get(Q(category_id=id) & Q(status='1'))

        # 获取该分类下的二级分类（最多 7 条）
        subcategories = category.subcategories.all()[:7]

        # 构造二级分类数据，并包含对应的商品数据
        subcategory_list = []
        for subcategory in subcategories:
            # 获取当前二级分类下的商品（最多 4 条）
            products = Product.objects.filter(sub_category_id=subcategory.sub_cate_id, status="1", is_deleted=False).order_by('?')[:4]
            product_list = [
                {
                    'id': str(product.product_id),
                    'name': product.product_name,
                    'price': str(product.price),
                    'images': [image for image in product.images if image][:1],
                }
                for product in products
            ]

            # 构造当前二级分类的数据，并包含商品列表
            subcategory_data = {
                "id": str(subcategory.sub_cate_id),
                "name": str(subcategory.sub_cate_name),
                "image": str(subcategory.sub_cate_image),
                "products": product_list  # 将商品列表添加到二级分类中
            }
            subcategory_list.append(subcategory_data)

        # 构造返回的数据
        category_data = {
            "id": str(category.category_id),
            "name": str(category.category_name),
            'images': category.category_images,
            "subcate": subcategory_list  # 包含商品列表的二级分类数据
        }

        result = Result.success_with_data(category_data)
        return JsonResponse(result.to_dict())

    except Category.DoesNotExist:
        result = Result.error("Category not found")
        return JsonResponse(result.to_dict(), status=404)
    
@require_POST
@token_required
@admin_required
def add_category_view(request):
    try:
        # 解析请求体中的 JSON 数据
        body = json.loads(request.body)
        category_name = body.get('name')  # 获取分类名称

        # 验证分类名称是否为空
        if not category_name:
            result = Result.error('Category name is required')
            return JsonResponse(result.to_dict(), status=400)

        # 创建新的一级分类
        new_category = Category.objects.create(
            category_id=uuid.uuid4(),  # 生成一个新的 UUID
            category_name=category_name,
            status="0"  # 默认状态为禁用
        )

        # 构造返回的数据
        category_data = {
            "id": str(new_category.category_id),
            "name": new_category.category_name,
            "status": new_category.status
        }

        result = Result.success_with_data(category_data)
        return JsonResponse(result.to_dict())

    except json.JSONDecodeError:
        result = Result.error('Invalid JSON format in request body')
        return JsonResponse(result.to_dict(), status=400)

@require_POST
@token_required
@admin_required
def update_category_view(request):
    try:
        # 解析请求体中的 JSON 数据
        body = json.loads(request.body)
        category_id = body.get('id')  # 获取分类 ID
        category_name = body.get('name')  # 获取新的分类名称
        status = body.get('status')  # 获取新的状态
        image_url = body.get('imageURL') #获取图片URL

        # 验证分类 ID 和名称是否为空
        if not category_id or (not category_name and not status):
            result = Result.error('Category ID and at least one of name or status are required')
            return JsonResponse(result.to_dict(), status=400)

        # 查找要更新的分类
        try:
            category = Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            result = Result.error('Category not found')
            return JsonResponse(result.to_dict(), status=404)

        # 更新分类信息
        if category_name:
            category.category_name = category_name
        if status:
            category.status = status
        if image_url is not None:  # 允许传递空数组来删除所有图片
            # 确保 image_url 是列表类型
            if not isinstance(image_url, list):
                result = Result.error('imageURL must be an array')
                return JsonResponse(result.to_dict(), status=400)
                
            # 删除旧的图片文件（假设图片存储在文件系统中）
            if category.category_images:
                
                for old_image_url in category.category_images:
                    try:
                        # 解析图片路径并删除文件
                        old_image_path = os.path.join(settings.MEDIA_ROOT, old_image_url)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    except Exception as e:
                        # 如果删除失败，记录日志但继续执行
                        logger.error(f'Failed to delete image {old_image_url}: {str(e)}')

            # 更新图片 URL
            category.category_images = image_url
        category.save()

        # 构造返回的数据
        category_data = {
            "id": str(category.category_id),
            "name": category.category_name,
            "status": category.status,
            "imageURL": category.category_images
        }

        result = Result.success_with_data(category_data)
        return JsonResponse(result.to_dict())

    except json.JSONDecodeError:
        result = Result.error('Invalid JSON format in request body')
        return JsonResponse(result.to_dict(), status=400)

@require_POST
@token_required
@admin_required
def delete_category_view(request):
    try:
        # 解析请求体中的 JSON 数据
        body = json.loads(request.body)
        category_id = body.get('id')  # 获取分类 ID

        # 验证分类 ID 是否为空
        if not category_id:
            result = Result.error('Category ID is required')
            return JsonResponse(result.to_dict(), status=400)

        # 查找要删除的分类
        try:
            category = Category.objects.get(category_id=category_id)
        except Category.DoesNotExist:
            result = Result.error('Category not found')
            return JsonResponse(result.to_dict(), status=404)

        # 检查是否存在关联的子分类
        if category.subcategories.exists():
            result = Result.error('Cannot delete category with associated subcategories')
            return JsonResponse(result.to_dict(), status=400)

        # 删除分类
        category.delete()

        result = Result.success_with_data('Category deleted successfully')
        return JsonResponse(result.to_dict())

    except json.JSONDecodeError:
        result = Result.error('Invalid JSON format in request body')
        return JsonResponse(result.to_dict(), status=400)
    
@token_required
@admin_required
@require_GET
def get_all_categories_view(request):
    categories = Category.objects.all()

    # 构造返回的数据
    category_list = [
        {
            "id": str(category.category_id),  # UUID 转换为字符串
            "name": category.category_name
        }
        for category in categories
    ]

    result = Result.success_with_data(category_list)
    return JsonResponse(result.to_dict())

@token_required
@admin_required
@require_GET
def get_admin_all_categories_view(request):
    try:
        page = int(request.GET.get('page', 1))  # 默认第一页
        page_size = int(request.GET.get('pageSize', 10))  # 默认每页10条

        # 计算分页范围
        start = (page - 1) * page_size
        end = start + page_size

        categories = Category.objects.all()[start:end]

        categories_data = [{
            'id': category.category_id,
            'name': category.category_name,
            'status': category.status,
            'imageURL': category.category_images,
        } for category in categories]

        result = Result.success_with_data(categories_data)
        return JsonResponse(result.to_dict())
    
    except ValueError:
        result = Result.error('Invalid page or pageSize parameter')
        return JsonResponse(result.to_dict(), status=400)
    except Exception as e:
        result = Result.error(f'Failed to get products: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)