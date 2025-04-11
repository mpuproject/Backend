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
        # verify if the file exist
        if 'file' not in request.FILES:
            result = Result.error('No file provided')
            return JsonResponse(result.to_dict(), status=400)
        
        file = request.FILES['file']
        
        # verify MIME type
        if not file.content_type.startswith('image/'):
            result = Result.error('Only image files are allowed')
            return JsonResponse(result.to_dict(), status=400)
        
        # verify file extension
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in allowed_extensions:
            result = Result.error('Invalid file extension')
            return JsonResponse(result.to_dict(), status=400)
        
        # check the file size
        if file.size > 20 * 1024 * 1024:  # 5MB
            result = Result.error('File size must be less than 5MB')
            return JsonResponse(result.to_dict(), status=400)
        
        # check file content
        try:
            Image.open(file).verify()
        except Exception:
            result = Result.error('Invalid image file')
            return JsonResponse(result.to_dict(), status=400)
        
        try:
            img = Image.open(file)
            # 移除EXIF数据
            if 'exif' in img.info:
                img.info.pop('exif')
            
            # 创建新文件对象进行二次保存
            from io import BytesIO
            new_file = BytesIO()
            img.save(new_file, format=img.format, quality=85)
            new_file.seek(0)
            
            # 替换原始文件对象
            file.file = new_file
        except Exception as e:
            result = Result.error('Invalid image processing')
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