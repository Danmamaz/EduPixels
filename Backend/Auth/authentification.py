# your_auth_app/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import CustomUser

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token["user_id"]
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None
