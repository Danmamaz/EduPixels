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
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="courses"
    )
    topic = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.topic


class ModuleModel(models.Model):
    course = models.ForeignKey(
        CourseModel,
        on_delete=models.CASCADE,
        related_name="modules"
    )
    title = models.CharField(max_length=255)
    # Поле homework видалено, тепер це окрема сутність.
    # Менше сміття в таблиці модулів.

    def __str__(self):
        return self.title


class LessonModel(models.Model):
    module = models.ForeignKey(
        ModuleModel,
        on_delete=models.CASCADE,
        related_name="lessons"
    )
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    content = models.TextField()

    def __str__(self):
        return self.title


class HomeworkModel(models.Model):
    module = models.ForeignKey(
        ModuleModel,
        on_delete=models.CASCADE,
        related_name="homeworks"
    )
    title = models.CharField(max_length=255, default="Домашнє завдання")
    content = models.TextField(blank=True) # Саме завдання
    
    # === Нові поля для Code Review ===
    user_submission = models.TextField(blank=True, null=True) # Що накльопав юзер
    ai_feedback = models.TextField(blank=True, null=True)     # Що про це думає AI
    grade = models.IntegerField(blank=True, null=True)        # Оцінка (0-100)
    
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        status = "✅" if self.grade else "❌"
        return f"{status} HW: {self.title} ({self.module.title})"