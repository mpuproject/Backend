from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import os
import uuid
from common.result.result import Result
from django.views.decorators.csrf import csrf_exempt
from common.utils.decorators import token_required

@token_required
@csrf_exempt
@require_POST
def upload_image(request):
    try:
        # 获取上传的文件
        if 'file' not in request.FILES:
            result = Result.error('No file provided')
            return JsonResponse(result.to_dict(), status=400)
        
        file = request.FILES['file']
        
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            result = Result.error('Only image files are allowed')
            return JsonResponse(result.to_dict(), status=400)
        
        # 验证文件大小（限制为2MB）
        if file.size > 2 * 1024 * 1024:
            result = Result.error('File size must be less than 2MB')
            return JsonResponse(result.to_dict(), status=400)
        
        # 生成唯一文件名
        ext = os.path.splitext(file.name)[1]
        filename = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}{ext}"
        
        # 保存文件
        filepath = default_storage.save(filename, file)
        
        # 返回文件URL
        file_url = default_storage.url(filepath)
        return JsonResponse({'url': file_url}, status=201)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)