from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import os
import uuid
from PIL import Image
from common.result.result import Result
from common.utils.decorators import token_required

@token_required
@require_POST
def upload_image(request):
    try:
        # 检查文件是否存在
        if 'file' not in request.FILES:
            result = Result.error('No file provided')
            return JsonResponse(result.to_dict(), status=400)
        
        file = request.FILES['file']
        
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            result = Result.error('Only image files are allowed')
            return JsonResponse(result.to_dict(), status=400)
        
        # 验证文件扩展名
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            result = Result.error('Invalid file extension')
            return JsonResponse(result.to_dict(), status=400)
        
        # 验证文件大小
        if file.size > 5 * 1024 * 1024:  # 5MB
            result = Result.error('File size must be less than 5MB')
            return JsonResponse(result.to_dict(), status=400)
        
        # 检查文件内容
        try:
            Image.open(file).verify()  # 验证图片文件
        except Exception:
            result = Result.error('Invalid image file')
            return JsonResponse(result.to_dict(), status=400)
        
        # 生成唯一文件名
        filename = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}{ext}"
        
        # 保存文件
        filepath = default_storage.save(filename, file)
        
        # 返回文件URL
        file_url = request.build_absolute_uri(default_storage.url(filepath))
        return JsonResponse({'url': file_url}, status=201)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)