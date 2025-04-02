超级管理员账户
username: admin
password: MPU2025@


顾客账户
username: customer
password: Test1234@

管理员账户
username: admin1
password Test1234@


运行以下脚本以下载插件：

```shell
# 安装 Django
pip install django

# 安装 Django REST framework
pip install djangorestframework

# 安装 Django REST framework Simple JWT
pip install djangorestframework-simplejwt

# 安装 Django CORS Headers
pip install django-cors-headers

# 安装django_extensions
pip install django-extensions Werkzeug pyOpenSSL

# 使用以下命令开启后端
python manage.py runserver_plus --cert-file certs/localhost.pem --key-file certs/localhost-key.pem
```
