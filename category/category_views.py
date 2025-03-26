from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from .models import Category
from common.result.result import Result
import json
from product.models import Product
import uuid
from common.utils.decorators import token_required, admin_required

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

        try:
            uuid.UUID(id)
        except ValueError:
            result = Result.error("Invalid category ID format")
            return JsonResponse(result.to_dict(), status=400)

        # 获取分类信息
        category = Category.objects.get(category_id=id)

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
        image_url = body.get('image') #获取图片URL

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
        if image_url:
            category.image = image_url
        category.save()

        # 构造返回的数据
        category_data = {
            "id": str(category.category_id),
            "name": category.category_name,
            "status": category.status,
            "image": category.status
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

        # 删除分类
        category.delete()

        result = Result.success('Category deleted successfully')
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
            "name": category.category_name,
            "status": category.status,
            'images': category.category_images
        }
        for category in categories
    ]

    result = Result.success_with_data(category_list)
    return JsonResponse(result.to_dict())