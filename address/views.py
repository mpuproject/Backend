from .models import Address
from common.result.result import Result
from common.utils.decorators import token_required
from django.views.decorators.http import require_GET, require_POST, require_http_methods
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from user.models import User

@token_required
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
    
@token_required
@require_POST
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
        
        address = {
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
        addr = Address.objects.create(**address)

        address_data = {
            'id': addr.address_id,
            'tag': addr.address_tag,
            'recipient': addr.recipient_name,
            'phone': addr.phone,
            'province': addr.province,
            'city': addr.city,
            'district': addr.district,
            'additional_addr': addr.additional_address,
            'postal_code': addr.postal_code,
            'is_default': addr.is_default,
        }
        
        result = Result.success_with_data(address_data)
        return JsonResponse(result.to_dict(), status=201)
        
    except Exception as e:
        result = Result.error(f'Fail to add address: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)

@require_http_methods('PUT')
@token_required
def update_address_view(request):
    try:
        data = json.loads(request.body)
        address_id = data.get('addressId')
        
        if not address_id:
            result = Result.error('Address id missed')
            return JsonResponse(result.to_dict(), status=400)
        
        try:
            address = Address.objects.get(address_id=address_id)
        except Address.DoesNotExist:
            result = Result.error('Address not found')
            return JsonResponse(result.to_dict(), status=404)
            
        # 如果更新为默认地址，需要先取消其他默认地址
        if data.get('is_default', False):
            Address.objects.filter(user=address.user, is_default=True).update(is_default=False)
            
        # 更新地址信息
        address.address_tag = data.get('tag', address.address_tag)
        address.recipient_name = data.get('recipient', address.recipient_name)
        address.phone = data.get('phone', address.phone)
        address.province = data.get('province', address.province)
        address.city = data.get('city', address.city)
        address.district = data.get('district', address.district)
        address.additional_address = data.get('additional_addr', address.additional_address)
        address.postal_code = data.get('postal_code', address.postal_code)
        address.is_default = data.get('is_default', address.is_default)
        address.save()
        
        # 返回更新后的地址信息
        address_data = {
            'id': address.address_id,
            'tag': address.address_tag,
            'recipient': address.recipient_name,
            'phone': address.phone,
            'province': address.province,
            'city': address.city,
            'district': address.district,
            'additional_addr': address.additional_address,
            'postal_code': address.postal_code,
            'is_default': address.is_default,
        }
        
        result = Result.success_with_data(address_data)
        return JsonResponse(result.to_dict())
        
    except Exception as e:
        result = Result.error(f'Fail to update address: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
     
@require_http_methods('DELETE')
@token_required
def delete_address_view(request):
    try:
        data = json.loads(request.body)
        address_id = data.get('addressId')
        
        if not address_id:
            result = Result.error('Address id missed')
            return JsonResponse(result.to_dict(), status=400)
        
        try:
            address = Address.objects.get(address_id=address_id)
        except Address.DoesNotExist:
            result = Result.error('Address not found')
            return JsonResponse(result.to_dict(), status=404)
            
        # 如果删除的是默认地址，且用户还有其他地址
        if address.is_default:
            other_addresses = Address.objects.filter(user=address.user).exclude(address_id=address_id)
            if other_addresses.exists():
                # 将第一个其他地址设置为默认地址
                new_default_address = other_addresses.first()
                new_default_address.is_default = True
                new_default_address.save()
        
        # 删除地址
        address.delete()
        
        result = Result.success('Address deleted successfully')
        return JsonResponse(result.to_dict())
        
    except Exception as e:
        result = Result.error(f'Fail to delete address: {str(e)}')
        return JsonResponse(result.to_dict(), status=500)
