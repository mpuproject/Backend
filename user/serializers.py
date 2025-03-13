from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime, timedelta, timezone

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['phone'] = user.phone
        token['is_staff'] = user.is_staff
        
        # 如果用户是staff，设置token有效期为1天
        if user.is_staff:
            token.set_exp(from_time=datetime.now(timezone.utc), lifetime=timedelta(days=1))
        
        return token

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.token_class(attrs['refresh'])

        # 从 refresh token 中获取自定义字段
        email = refresh.payload.get('email')
        phone = refresh.payload.get('phone')
        is_staff = refresh.payload.get('is_staff')

        # 将自定义字段添加到新的 access token 中
        access = AccessToken(data['access'])
        if email is not None:
            access['email'] = email
        if phone is not None:
            access['phone'] = phone
        if is_staff is not None:
            access['is_staff'] = is_staff

        data['access'] = str(access)
        return data