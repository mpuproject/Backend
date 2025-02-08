from .models import Address
from common.result.result import Result
from common.utils.decorators import token_required
from django.views.decorators.http import require_GET, require_POST, require_http_methods
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from user.models import User

# @token_required
@require_GET
def get_address_view(request):
    user_id = request.GET.get('id')
    if not user_id:
        result = Result.error("User id missed")
        return JsonResponse(result, status=400)
    
    try:
        addressList = Address.objects.filter(user=user_id)
        address_data = [{
            'id': address.address_id,
            'tag': address.address_tag,
            'recipient': address.recipient_name,
            'phone': address.phone,
            'province': address.province,
            'city': address.city,
            'district': address.district,
            'additional_addr': address.additional_address,
            'postal_code': address.postal_code,
            'is_default': address.is_default
        } for address in addressList]
        result = Result.success_with_data(address_data)
        return JsonResponse(result.to_dict())
    except Address.DoesNotExist:
        result = Result.error('Address not found')
        return JsonResponse(result.to_dict())
    
# @token_required
@require_POST
@csrf_exempt
def add_address_view(request):

    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        if not user_id:
            result = Result.error('User id missed')
            return JsonResponse(result.to_dict(), status=400)
        
        try:
            # 获取User实例
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            result = Result.error('User does not exist')
            return JsonResponse(result.to_dict(), status=404)
        
        # 检查用户地址数量是否超过限制
        address_count = Address.objects.filter(user=user).count()
        if address_count >= 5:
            result = Result.error('Each user can create up to 5 addresses')
            return JsonResponse(result.to_dict(), status=400)
            
        # 检查用户是否已有地址
        has_existing_address = address_count > 0
        
        address_data = {
            'user': user,
            'address_tag': data.get('tag', ''),
            'recipient_name': data.get('recipient'),
            'phone': data.get('phone'),
            'province': data.get('province'),
            'city': data.get('city'),
            'district': data.get('district'),
            'additional_address': data.get('additional_addr'),
            'postal_code': data.get('postal_code', '000000'),
            'is_default': not has_existing_address
        }
        
        # 创建新地址
        Address.objects.create(**address_data)
        
        result = Result.success()
        return JsonResponse(result.to_dict(), status=201)
        
    except Exception as e:
        result = Result.error(f'Fail to add address: {str(e)}')
        return JsonResponse(result.to_dict(), status=500) 