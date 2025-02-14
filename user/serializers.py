from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['is_staff'] = user.is_staff
        print(token)
        return token

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.token_class(attrs['refresh'])

        # 从refresh token中获取自定义字段
        email = refresh.payload.get('email')
        is_staff = refresh.payload.get('is_staff')

        # 将自定义字段添加到新的access token中
        access = AccessToken(data['access'])
        if email is not None:
            access['email'] = email
        if is_staff is not None:
            access['is_staff'] = is_staff

        data['access'] = str(access)
        return data