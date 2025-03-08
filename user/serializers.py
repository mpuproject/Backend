from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime, timedelta
from rest_framework import serializers

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['iat'] = datetime.now()   #签发时间
        token['exp'] = datetime.now() + timedelta(minutes=15)  #过期时间
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        return token

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.token_class(attrs['refresh'])

        # 验证 token 是否在有效期内
        now = datetime.now()
        iat = refresh.payload.get('iat')
        exp = refresh.payload.get('exp')

        if iat is None or exp is None:
            raise serializers.ValidationError('Token is missing iat or exp field')

        # 将 iat 和 exp 转换为 datetime 对象
        iat_time = datetime.fromtimestamp(iat)
        exp_time = datetime.fromtimestamp(exp)

        # 检查 token 是否已过期
        if now > exp_time:
            raise serializers.ValidationError('Token has expired')

        # 检查 token 是否已生效
        if now < iat_time:
            raise serializers.ValidationError('Token is not yet valid')

        # 从 refresh token 中获取自定义字段
        email = refresh.payload.get('email')
        is_staff = refresh.payload.get('is_staff')

        # 将自定义字段添加到新的 access token 中
        access = AccessToken(data['access'])
        if email is not None:
            access['email'] = email
        if is_staff is not None:
            access['is_staff'] = is_staff

        # 更新 access token 的 iat 和 exp
        access['iat'] = now
        access['exp'] = now + timedelta(minutes=15)

        data['access'] = str(access)
        return data