from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.http import JsonResponse
from common.result.result import Result
from .models import Product
from django.db.models import Q, Value, F
from rest_framework.views import APIView
from category.models import SubCategory, Category
from django.views.decorators.csrf import csrf_exempt
import uuid
import json
from django.utils import timezone
from common.utils.decorators import admin_required, token_required

@require_GET
def get_details_view(request, pk):  # 使用 pk 作为参数名
    try:
        # 使用 pk 查询商品
        product = Product.objects.get(pk=pk, status='1')
    except Product.DoesNotExist:
        result = Result.error('Product does not exist')
        return JsonResponse(result.to_dict(), status=404)

    # 获取商品的二级分类
    sub_category = product.sub_category

    # 获取二级分类对应的一级分类
    category = sub_category.category

    # 构造商品数据
    product_data = {
        'id': str(product.product_id),
        'name': product.product_name,
        'price': str(product.price),
        'description': product.product_desc,
        'rating': product.product_rating,
        'stock_quantity': product.stock_quantity,
        'low_stock_threshold': product.low_stock_threshold,
        'images': product.images,
        'details': product.product_details,
        'sub_category': {
            'id': str(sub_category.sub_cate_id),
            'name': sub_category.sub_cate_name,
        },
        'category': {
            'id': str(category.category_id),
            'name': category.category_name,
        },
    }

    result = Result.success_with_data(product_data)
    return JsonResponse(result.to_dict())

# 查询相关产品
class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')  # 搜索关键词
        category_id = request.query_params.get('category', None)  # 一级分类 ID
        page = request.query_params.get('page', 1)  # 当前页码
        page_size = request.query_params.get('pageSize', 10)  # 每页大小
        sort_field = request.query_params.get('sortField', 'created_time')  # 按何种搜索方法排序

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            result = Result.error('Invalid page or pageSize parameter')
            return JsonResponse(result.to_dict(), status=400)

        # 初始化产品查询集
        products = Product.objects.all(status='1')

        # 如果提供了一级分类 ID
        if category_id:
            # 查找该一级分类关联的所有二级分类 ID
            sub_category_ids = SubCategory.objects.filter(
                category__category_id=category_id
            ).values_list('sub_cate_id', flat=True)

            # 过滤出关联了这些二级分类 ID 的产品
            products = products.filter(sub_category__sub_cate_id__in=sub_category_ids)

        # 模糊查询商品名称和商品描述，筛选可用和没存货的商品
        if query:
            # 计算相关度分数
            products = products.annotate(
                relevance_score=(
                    F('product_name__icontains', Value(query)) * 2 +  # 产品名称相关度权重更高
                    F('product_desc__icontains', Value(query)) * 1    # 产品描述相关度权重较低
                )
            ).filter(
                (Q(product_name__icontains=query) | Q(product_desc__icontains=query)) &
                (Q(status='ACT') | Q(status='OOS'))
            ).order_by('-relevance_score', f'-{sort_field}')  # 先按相关度排序，再按其他字段排序

        # 分页
        start = (page - 1) * page_size
        end = start + page_size
        paginated_products = products[start:end]

        # 格式化结果
        products_data = []
        for product in paginated_products:
            products_data.append({
                'id': product.product_id,
                'name': product.product_name,
                'description': product.product_desc,
                'price': str(product.price),
                'images': product.images[0],
                'sub_category': product.sub_category.sub_cate_name,
                'category': product.sub_category.category.category_name,
            })

        result = Result.success_with_data({
            'total': products.count(),
            'products': products_data
        })
        return JsonResponse(result.to_dict())

@token_required
@admin_required
@csrf_exempt
@require_POST
def add_product_view(request):
    try:
        # 解析请求体中的JSON数据
        data = json.loads(request.body)
        
        # 自动生成产品ID
        product_id = str(uuid.uuid4())
        
        # 创建产品对象
        product = Product(
            product_id=product_id,
            product_name=data['name'],
            price=data['price'],
            product_desc=data['description'],
            stock_quantity=data['stockQuantity'],
            low_stock_threshold=data['lowStockThreshold'],
            images=data['images'],
            status=data['status'],
            sub_category_id=data['subCategoryId'],
            product_rating=0,
            product_details=data.get('details', ''),  # 如果未提供details，默认为空字符串
            created_time=timezone.now()
        )
        
        # 保存产品
        product.save()
        
        result = Result.success_with_data({'id': product_id})
        return JsonResponse(result.to_dict(), status=201)
    
    except KeyError as e:
        result = Result.error(f'Missing required field: {str(e)}')
        return JsonResponse(result.to_dict(), status=400)
    except Exception as e:
        result = Result.error(f'Failed to add product: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)

@token_required
@admin_required
@csrf_exempt
@require_http_methods(['PUT'])
def update_product_view(request, id):
    try:
        # 解析请求体中的JSON数据
        data = json.loads(request.body)
        
        # 获取产品对象
        try:
            product = Product.objects.get(product_id=id)
        except Product.DoesNotExist:
            result = Result.error('Product does not exist')
            return JsonResponse(result.to_dict(), status=404)
        
        # 更新可修改的字段
        if 'name' in data:
            product.product_name = data['name']
        if 'price' in data:
            product.price = data['price']
        if 'description' in data:
            product.product_desc = data['description']
        if 'stock_quantity' in data:
            product.stock_quantity = data['stockQuantity']
        if 'low_stock_threshold' in data:
            product.low_stock_threshold = data['lowStockThreshold']
        if 'images' in data:
            product.images = data['images']
        if 'sub_category_id' in data:
            product.sub_category = data['subCategoryId']
        if 'details' in data:
            product.product_details = data['details']
        product.updated_time = timezone.now()
        
        # 保存更新
        product.save()
        
        result = Result.success()
        return JsonResponse(result.to_dict())
    
    except Exception as e:
        result = Result.error(f'Failed to update product: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)

@admin_required
@token_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_product_view(request, id):
    try:
        # 获取并删除产品对象
        try:
            product = Product.objects.get(product_id=id)
            product.delete()
        except Product.DoesNotExist:
            result = Result.error('Product does not exist')
            return JsonResponse(result.to_dict(), status=404)
        
        result = Result.success()
        return JsonResponse(result.to_dict())
    
    except Exception as e:
        result = Result.error(f'Failed to delete product: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
    
@admin_required
@token_required
@require_GET
def get_product_view(request):
    try:
        page = int(request.GET.get('page', 1))  # 默认第一页
        page_size = int(request.GET.get('pageSize', 20))  # 默认每页20条

        # 计算分页范围
        start = (page - 1) * page_size
        end = start + page_size
        
        # 获取分页后的产品数据
        products = Product.objects.all()[start:end]
        
        # 格式化产品数据
        products_data = [{
            'id': product.product_id,
            'name': product.product_name,
            'price': str(product.price),
            'status': product.status,
            'stock_quantity': product.stock_quantity,
            'low_stock_threshold': product.low_stock_threshold,
            'description': product.product_desc,
            'rating': product.product_rating,
            'images': product.images,
            'subcategory': product.sub_category.sub_cate_name,
            'category': product.sub_category.category.category_name,
            'createdTime': product.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            'updatedTime': product.updated_time.strftime('%Y-%m-%d %H:%M:%S'),
        } for product in products]
        
        # 返回分页结果
        result = Result.success_with_data({
            'total': Product.objects.count(),  # 总记录数
            'products': products_data
        })
        return JsonResponse(result.to_dict())
    
    except ValueError:
        result = Result.error('Invalid page or pageSize parameter')
        return JsonResponse(result.to_dict(), status=400)
    except Exception as e:
        result = Result.error(f'Failed to get products: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)