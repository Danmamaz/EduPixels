from rest_framework import serializers
from .models import ChatPrompt

class ChatPromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatPrompt
        fields = ['id', 'user_input', 'created_at']
        read_only_fields = ['id', 'created_at']
