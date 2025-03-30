from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from .models import SubCategory
from common.result.result import Result
import json
from product.models import Product
from django.core.paginator import Paginator
from common.utils.decorators import admin_required, token_required
import logging

logger = logging.getLogger(__name__)

# 获取二级分类导航
@require_GET
def get_subcategory_filter_view(request, id):
    try:
        # 获取二级分类信息
        subCategory = SubCategory.objects.get(sub_cate_id=id)
        
        sub_category_data = {
            "id": subCategory.sub_cate_id,
            "name": subCategory.sub_cate_name,
            "categoryId": subCategory.category.category_id,
            "categoryName": subCategory.category.category_name
        }

        #组装返回数据
        result = Result.success_with_data(sub_category_data)
        return JsonResponse(result.to_dict())

    except SubCategory.DoesNotExist:
        result = Result.error("Sub-category not found")
        return JsonResponse(result.to_dict(), status=404)
    
@require_POST
def get_subcategory_products_view(request):
    try:
        # 解析请求体中的 JSON 数据
        body = json.loads(request.body)
        sub_category_id = body.get('subCategoryId')  # 二级分类 ID
        page = body.get('page', 1)  # 当前页码，默认为 1
        page_size = body.get('pageSize', 20)  # 每页数量，默认为 20
        sort_field = body.get('sortField', 'default')  # 排序字段，默认为 created_time
        min_price = body.get('sortMin')  # 最小价格
        max_price = body.get('sortMax')  # 最大价格

        # 验证二级分类是否存在
        try:
            sub_category = SubCategory.objects.get(sub_cate_id=sub_category_id)
        except SubCategory.DoesNotExist:
            result = Result.error("Subcategory not found")
            return JsonResponse(result.to_dict(), status=404)

        products = Product.objects.filter(
                sub_category=sub_category, 
                status='1', 
                is_deleted=False
            )

        # 添加价格区间筛选
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        # 获取二级分类下的所有可用产品，并按指定字段排序
        if sort_field == 'created_time':
            products = products.order_by(f'-{sort_field}')
        elif sort_field == 'product_rating':
            products = products.order_by(f'-{sort_field}')
        elif 'price' in sort_field:
            products = products.order_by(f'{sort_field}')
        

        # 分页处理
        paginator = Paginator(products, page_size)

        # 若大于总页数：
        if page > paginator.num_pages:
            response_data = {
                "products": [],
                "pagination": {
                    "current_page": page,
                    "total_pages": paginator.num_pages,
                    "total_items": paginator.count,
                    "page_size": page_size
                }
            }
            result = Result.success_with_data(response_data)
            return JsonResponse(result.to_dict())

        page_obj = paginator.get_page(page)

        # 构造返回的数据
        product_list = [
            {
                "id": str(product.product_id),
                "name": product.product_name,
                "price": str(product.price),
                "images": [image for image in product.images if image][:1], #筛选掉空的字符串，并保留第一张
                "created_time": product.created_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            for product in page_obj
        ]

        # 返回分页信息和产品列表
        response_data = {
            "products": product_list,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "page_size": page_size
            }
        }

        result = Result.success_with_data(response_data)
        return JsonResponse(result.to_dict())

    except json.JSONDecodeError:
        result = Result.error("Invalid JSON format in request body")
        return JsonResponse(result.to_dict(), status=400)

@require_GET    
@token_required
@admin_required
def get_subcategory_view(request):
    subList = SubCategory.objects.all()
    
    subcategory_data = [
        {
            "id": sub.sub_cate_id,
            "name": sub.sub_cate_name,
            "category_id": sub.category.category_id,
        }
        for sub in subList
    ]

    result = Result.success_with_data(subcategory_data)
    return JsonResponse(result.to_dict())

@require_GET
@token_required
@admin_required
def get_admin_subcategory_view(request):
    try:
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 10))
        
        # 限制 page_size 的最大值
        if page_size > 50:
            page_size = 50

        # 使用 Paginator 处理分页
        paginator = Paginator(SubCategory.objects.all(), page_size)
        page_obj = paginator.get_page(page)

        # 构造返回数据
        subcategories_data = [{
            'id': subcategory.sub_cate_id,
            'name': subcategory.sub_cate_name,
            'status': subcategory.status,
            'images': subcategory.sub_cate_image if subcategory.sub_cate_image else "",  # 直接返回完整的字符串
            'categoryId': str(subcategory.category.category_id)  # 确保 categoryId 是字符串
        } for subcategory in page_obj]

        # 确保 subcategories_data 是有效的列表
        if not isinstance(subcategories_data, list):
            raise ValueError("subcategories_data must be a list")

        result_data = {
            'data': subcategories_data,
            'total': paginator.count
        }
        # 返回结果
        result = Result.success_with_data(result_data)
        return JsonResponse(result.to_dict())
    
    except ValueError as e:
        logger.error(f"ValueError in get_admin_subcategory_view: {str(e)}")
        result = Result.error('Invalid page or pageSize parameter')
        return JsonResponse(result.to_dict(), status=400)
    except Exception as e:
        logger.error(f"Exception in get_admin_subcategory_view: {str(e)}")
        result = Result.error(f'Failed to get subcategories: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
    

@require_POST
@token_required
@admin_required
def add_subcategory_view(request):
    try:
        # 解析请求体中的 JSON 数据
        body = json.loads(request.body)
        sub_cate_name = body.get('name')  # 获取二级分类名称
        category_id = body.get('categoryId')  # 获取所属一级分类ID
        image_url = body.get('images')  # 获取图片URL

        # 验证必填字段
        if not sub_cate_name or not category_id:
            result = Result.error('Subcategory name and category ID are required')
            return JsonResponse(result.to_dict(), status=400)

        # 验证图片URL是否为列表类型
        if image_url and not isinstance(image_url, list):
            result = Result.error('imageURL must be an array')
            return JsonResponse(result.to_dict(), status=400)

        # 创建新的二级分类
        new_subcategory = SubCategory.objects.create(
            sub_cate_name=sub_cate_name,
            category_id=category_id,
            sub_cate_image=image_url if image_url else [],
            status="0"  # 默认状态为禁用
        )

        # 构造返回的数据
        subcategory_data = {
            "id": new_subcategory.sub_cate_id,
            "name": new_subcategory.sub_cate_name,
            "categoryId": new_subcategory.category.category_id,
            "imageURL": new_subcategory.sub_cate_image,
            "status": new_subcategory.status
        }

        result = Result.success_with_data(subcategory_data)
        return JsonResponse(result.to_dict())

    except json.JSONDecodeError:
        result = Result.error('Invalid JSON format in request body')
        return JsonResponse(result.to_dict(), status=400)
    except Exception as e:
        result = Result.error(f'Failed to add subcategory: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
    
@require_http_methods('PUT')
@token_required
@admin_required
def update_subcategory_view(request):
    try:
        body = json.loads(request.body)
        sub_cate_id = body.get('id')  # 获取二级分类ID
        sub_cate_name = body.get('name')  # 获取二级分类名称
        category_id = body.get('categoryId')  # 获取所属一级分类ID
        image_url = body.get('images')  # 获取图片URL
        status = body.get('status')  # 获取状态

        # 验证必填字段
        if not sub_cate_id:
            result = Result.error('Subcategory ID is required')
            return JsonResponse(result.to_dict(), status=400)

        # 查找要更新的二级分类
        try:
            subcategory = SubCategory.objects.get(sub_cate_id=sub_cate_id)
        except SubCategory.DoesNotExist:
            result = Result.error('Subcategory not found')
            return JsonResponse(result.to_dict(), status=404)

        # 更新字段
        if sub_cate_name:
            subcategory.sub_cate_name = sub_cate_name
        if category_id:
            subcategory.category_id = category_id
        if image_url is not None:  # 允许传递空字符串来删除图片
            if not isinstance(image_url, str):  # 检查是否为字符串
                result = Result.error('imageURL must be a string')
                return JsonResponse(result.to_dict(), status=400)
            subcategory.sub_cate_image = image_url  # 直接存储为字符串
        if status is not None:
            subcategory.status = status

        # 保存更新
        subcategory.save()

        # 构造返回的数据
        subcategory_data = {
            "id": subcategory.sub_cate_id,
            "name": subcategory.sub_cate_name,
            "categoryId": subcategory.category.category_id,
            "images": subcategory.sub_cate_image,  # 直接返回字符串
            "status": subcategory.status
        }

        result = Result.success_with_data(subcategory_data)
        return JsonResponse(result.to_dict())

    except json.JSONDecodeError:
        result = Result.error('Invalid JSON format in request body')
        return JsonResponse(result.to_dict(), status=400)
    except Exception as e:
        result = Result.error(f'Failed to update subcategory: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
    

@require_http_methods('DELETE')
@token_required
@admin_required
def delete_subcategory_view(request):
    try:
        # 解析请求体中的 JSON 数据
        body = json.loads(request.body)
        sub_cate_id = body.get('id')  # 获取二级分类ID

        # 验证分类 ID 是否为空
        if not sub_cate_id:
            result = Result.error('Subcategory ID is required')
            return JsonResponse(result.to_dict(), status=400)

        # 查找要删除的二级分类
        try:
            subcategory = SubCategory.objects.get(sub_cate_id=sub_cate_id)
        except SubCategory.DoesNotExist:
            result = Result.error('Subcategory not found')
            return JsonResponse(result.to_dict(), status=404)

        # 检查是否存在关联的商品
        if Product.objects.filter(sub_category=subcategory).exists():
            result = Result.error('Cannot delete subcategory with associated products')
            return JsonResponse(result.to_dict(), status=400)

        # 删除二级分类
        subcategory.delete()

        result = Result.success_with_data('Subcategory deleted successfully')
        return JsonResponse(result.to_dict())

    except json.JSONDecodeError:
        result = Result.error('Invalid JSON format in request body')
        return JsonResponse(result.to_dict(), status=400)
    except Exception as e:
        result = Result.error(f'Failed to delete subcategory: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
    