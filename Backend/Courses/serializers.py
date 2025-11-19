from rest_framework import serializers

class CoursePromptSerializer(serializers.Serializer):
    prompt = serializers.CharField(max_length=1024)
