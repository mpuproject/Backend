from django.http import JsonResponse
import json
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from common.result.result import Result
from user.models import User
from .models import Cart

@require_POST
@csrf_exempt
def save_cart_view(request):
    try:
        data = json.loads(request.body)
        user_id = data.get('user')
        products = data.get('products')

        if not user_id or not products:
            result = Result.error('Missing user or products')
            return JsonResponse(result.to_dict(), status=400)
        
        user = User.objects.get(id=user_id)
        cart, created = Cart.objects.get_or_create(user=user)
        cart.products = products
        cart.save()

        result = Result.success()
        return JsonResponse(result.to_dict())
    
    except User.DoesNotExist:
        result = Result.error('User not found')
        return JsonResponse(result.to_dict(), status=404)