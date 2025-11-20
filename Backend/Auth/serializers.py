# your_auth_app/serializers.py
from rest_framework import serializers
from .models import CustomUser
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def validate_password(self, value):
        if len(value) > 48:
            raise serializers.ValidationError("Password must be at most 48 characters long.")
        if len(value) < 8:
            raise serializers.ValidationError("Password must be minimum 8 characters.")
        # simple emoji check: allow only basic printable characters
        if not re.match(r'^[\x20-\x7E]+$', value):
            raise serializers.ValidationError("Password contains invalid characters (no emojis allowed).")
        return value

    def validate_email(self, value):
        # very basic check for '@' and '.'
        if '@' not in value or '.' not in value.split('@')[-1]:
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user