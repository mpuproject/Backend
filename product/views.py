from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from common.result.result import Result
from .models import Product
from django.db.models import Q, Value
from django.db.models import Case, When, IntegerField
from rest_framework.views import APIView
from category.models import SubCategory, Category

@require_GET
def get_details_view(request, pk):  # 使用 pk 作为参数名
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

class SearchView(APIView):
    def get(self, request):
        query = request.query_params.get('q', '')  # 搜索关键词
        category_id = request.query_params.get('category', None)  # 一级分类 ID
        page = request.query_params.get('page', 1)  # 当前页码
        page_size = request.query_params.get('pageSize', 10)  # 每页大小
        print(query=='')
        print(category_id==None)
        print(page)
        print(page_size)

        try:
            page = int(page)
            page_size = int(page_size)
        except ValueError:
            result = Result.error('Invalid page or pageSize parameter')
            return JsonResponse(result.to_dict(), status=400)

        # 初始化产品查询集
        products = Product.objects.all()

        # 如果提供了一级分类 ID
        if category_id:
            # 查找该一级分类关联的所有二级分类 ID
            sub_category_ids = SubCategory.objects.filter(
                category__category_id=category_id
            ).values_list('sub_cate_id', flat=True)

            # 过滤出关联了这些二级分类 ID 的产品
            products = products.filter(sub_category__sub_cate_id__in=sub_category_ids)

        # 模糊查询商品名称和商品描述
        if query:
            products = products.filter(
                Q(product_name__icontains=query) | Q(product_desc__icontains=query)
            )

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