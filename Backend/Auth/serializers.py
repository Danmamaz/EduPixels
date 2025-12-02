from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomUser
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def validate_password(self, value):
        if len(value) > 48:
            raise serializers.ValidationError("Password is too long.")
        if len(value) < 8:
            raise serializers.ValidationError("Password is too short.")
        if not re.match(r'^[\x20-\x7E]+$', value):
            raise serializers.ValidationError("Invalid characters.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        return {
            "token": data["access"]
        }