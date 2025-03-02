from django.views.decorators.http import require_GET, require_POST, require_http_methods
from django.http import JsonResponse
from common.result.result import Result
from .models import Product
from django.db.models import Q, F, Case, When, Value, IntegerField
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
        product = Product.objects.get(pk=pk, status='1', is_deleted=False)
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
        'createdTime': str(product.created_time),
        'updatedTime': str(product.updated_time),
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
        sort_field = request.query_params.get('sortField', 'default')  # 按何种搜索方法排序
        min_price = request.query_params.get('sortMin')  # 最小价格
        max_price = request.query_params.get('sortMax')  # 最大价格

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            result = Result.error('Invalid page or pageSize parameter')
            return JsonResponse(result.to_dict(), status=400)

        # 初始化产品查询集
        products = Product.objects.all().filter(status='1', is_deleted=False)

        # 如果提供了一级分类 ID
        if category_id:
            # 查找该一级分类关联的所有二级分类 ID
            sub_category_ids = SubCategory.objects.filter(
                category__category_id=category_id
            ).values_list('sub_cate_id', flat=True)

            # 过滤出关联了这些二级分类 ID 的产品
            products = products.filter(sub_category__sub_cate_id__in=sub_category_ids)

        # 使用 Q 对象进行模糊查询
        if query:
            products = products.annotate(
                search_priority=Case(
                    When(product_name__icontains=query, then=Value(2)),
                    When(product_desc__icontains=query, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            ).filter(Q(product_name__icontains=query) | Q(product_desc__icontains=query))

        # 添加价格区间筛选
        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

        if sort_field == 'created_time':
            products = products.order_by(f'-{sort_field}')
        elif sort_field == 'product_rating':
            products = products.order_by(f'-{sort_field}')
        elif 'price' in sort_field:
            products = products.order_by(f'{sort_field}')

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

@require_POST
@token_required
@admin_required
@csrf_exempt
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
            product_details=data.get('details', []),  # 如果未提供details，默认为空数组
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

@require_http_methods(['PUT'])
@token_required
@admin_required
@csrf_exempt
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
            product.stock_quantity += data['stock_quantity']
        if 'low_stock_threshold' in data:
            product.low_stock_threshold = data['low_stock_threshold']
        if 'images' in data:
            product.images = data['images']
        if 'sub_category' in data:
            sub_id = data['sub_category'][1]
            subCate = SubCategory.objects.get(sub_cate_id = sub_id)
            product.sub_category = subCate
        if 'details' in data:
            product.product_details = data['details']
        if 'status' in data:
            product.status = data['status']
        product.updated_time = timezone.now()
        
        # 保存更新
        product.save()
        
        result = Result.success()
        return JsonResponse(result.to_dict())
    
    except Exception as e:
        result = Result.error(f'Failed to update product: {str(e)}')
        print(str(e))
        return JsonResponse(result.to_dict(), status=500)

@require_http_methods(["PATCH"])
@token_required
@admin_required
@csrf_exempt
def delete_product_view(request, id):
    try:
        # 获取产品对象
        try:
            product = Product.objects.get(product_id=id)
            product.is_deleted = True  # 逻辑删除，将 is_deleted 设置为 True
            product.save()  # 保存更改
        except Product.DoesNotExist:
            result = Result.error('Product does not exist')
            return JsonResponse(result.to_dict(), status=404)
        
        result = Result.success()
        return JsonResponse(result.to_dict())
    
    except Exception as e:
        result = Result.error(f'Failed to delete product: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
    
@require_GET
@token_required
@admin_required
def get_product_view(request):
    try:
        query = request.GET.get('q', '')
        page = int(request.GET.get('page', 1))  # 默认第一页
        page_size = int(request.GET.get('pageSize', 10))  # 默认每页10条

        # 计算分页范围
        start = (page - 1) * page_size
        end = start + page_size
        
        # 获取基础查询集
        products = Product.objects.filter(is_deleted=False)
        
        # 如果存在查询参数，进行模糊查询
        if query:
            products = products.filter(
                Q(product_id__icontains=query) | 
                Q(product_name__icontains=query)
            )
        
        # 获取分页后的产品数据
        paginated_products = products[start:end]
        
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
        } for product in paginated_products]
        
        # 返回分页结果
        result = Result.success_with_data({
            'total': products.count(),  # 使用过滤后的总数
            'products': products_data
        })
        return JsonResponse(result.to_dict())
    
    except ValueError:
        result = Result.error('Invalid page or pageSize parameter')
        return JsonResponse(result.to_dict(), status=400)
    except Exception as e:
        result = Result.error(f'Failed to get products: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
    
@require_GET
@token_required
@admin_required
def get_product_inventory_status_view(request):
    # 获取库存紧张的产品
    low_stock_products = Product.objects.filter(
        stock_quantity__gt=0,
        stock_quantity__lt=F('low_stock_threshold'),
        status='1'
    ).count()
        
    # 获取库存不足的产品
    out_of_stock_products = Product.objects.filter(
        stock_quantity=0,
        status='1'
    ).count()

    data = {
        "understock": out_of_stock_products,
        "shortstock": low_stock_products,
    }
    result = Result.success_with_data(data)
    return JsonResponse(result.to_dict())

@require_GET
@token_required
@admin_required
def get_admin_product_view(request, pk):
    try:
        # 使用 pk 查询商品
        product = Product.objects.get(pk=pk)
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
        'status': product.status,
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
        'createdTime': str(product.created_time),
        'updatedTime': str(product.updated_time),
    }

    result = Result.success_with_data(product_data)
    return JsonResponse(result.to_dict())

@require_GET
def get_product_recommend_view(request):
    try:
        # 获取查询参数
        query = request.GET.get('name', '')
        product_id = request.GET.get('id')  # 新增：获取当前产品ID
        if not query or not product_id:
            result = Result.error('Query parameter and product_id are required')
            return JsonResponse(result.to_dict(), status=400)

        # 按空格分割查询字符串
        keywords = query.split()
        
        # 初始化查询集，排除当前产品
        products = Product.objects.filter(status='1', is_deleted=False).exclude(product_id=product_id)
        
        # 对每个关键词进行模糊查询
        all_results = []
        for keyword in keywords:
            # 使用 Q 对象进行模糊查询
            matched_products = products.filter(Q(product_name__icontains=keyword))
            all_results.extend(matched_products)
        
        # 去重
        unique_results = list(set(all_results))
        
        # 如果结果不足4个，返回所有结果
        if len(unique_results) <= 4:
            selected_products = unique_results
        else:
            # 随机选取4个产品
            import random
            selected_products = random.sample(unique_results, 4)
        
        # 格式化结果
        products_data = []
        for product in selected_products:
            products_data.append({
                'id': product.product_id,
                'name': product.product_name,
                'description': product.product_desc,
                'price': str(product.price),
                'images': product.images[0] if product.images else '',
                'sub_category': product.sub_category.sub_cate_name,
                'category': product.sub_category.category.category_name,
            })

        result = Result.success_with_data(products_data)
        return JsonResponse(result.to_dict())

    except Exception as e:
        result = Result.error(f'Failed to get recommendations: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
    