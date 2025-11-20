from django.db import models
from Auth.models import CustomUser

class ChatPrompt(models.Model):
    user_input = models.TextField()
    input_tokens = models.IntegerField(blank=True, null=True)
    output_tokens = models.IntegerField(blank=True, null=True)
    total_tokens = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt: {self.user_input[:30]}..."


class CourseModel(models.Model):
    topic = models.CharField(max_length=80)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="courses", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic


class ModuleModel(models.Model):
    course = models.ForeignKey(CourseModel, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class LessonModule(models.Model):
    module = models.ForeignKey(ModuleModel, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=20, default="lecture")
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title