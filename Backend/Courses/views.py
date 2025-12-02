import os
from pathlib import Path
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
import json
from django.db import transaction

from .models import *
from .serializers import ChatPromptSerializer

# Load .env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)
api_key = os.environ.get("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OpenRouter API key not found.")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def safe_json_parse(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                cleaned = text[start:end]
                return json.loads(cleaned)
            raise ValueError("No JSON found")
        except Exception:
            raise ValueError("Model returned invalid JSON")


def create_course_from_json(user, course_json):
    if not user or not user.is_authenticated:
        raise ValueError("User must be authenticated")

    if isinstance(course_json, str):
        course_json = safe_json_parse(course_json)

    topic = course_json["meta"]["topic"]
    modules_data = course_json["modules"]

    with transaction.atomic():
        course = CourseModel.objects.create(topic=topic, owner=user)

        for module_data in modules_data:
            module = ModuleModel.objects.create(
                title=module_data.get("title", "Модуль"),
                course=course
            )
            for lesson_data in module_data.get("lessons", []):
                LessonModel.objects.create(
                    module=module,
                    title=lesson_data.get("title", "Урок"),
                    type=lesson_data.get("type", "lecture"),
                )

    return course


class ChatAPIView(APIView):
    """
    POST endpoint to generate a course structure.
    No limits, no economy. Pure creation.
    """

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Більше ніяких перевірок балансу!
        
        user_input = request.data.get("prompt")
        if not user_input:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Логування запиту залишаємо чисто для історії (це не впливає на логіку)
        chat_entry = ChatPrompt.objects.create(user_input=user_input)

        try:
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini", 
                temperature=0.7,
                max_tokens=4000, # Ліміт самого провайдера, щоб не зловити 402
                response_format={ "type": "json_object" }, 
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are a high-level curriculum design AI. 
                        OUTPUT MUST BE VALID JSON IN UKRAINIAN.

                        INPUT FORMAT (JSON):
                        { "topic": "string" }

                        OUTPUT FORMAT (strict JSON, Ukrainian only):
                        {
                            "meta": { "topic": "Course Name" },
                            "modules": [
                                {
                                    "title": "Module Title",
                                    "lessons": [
                                        { "title": "Lesson Title", "type": "lecture" }
                                    ]
                                }
                            ]
                        }

                        RULES:
                        1. Topic: IT related only.
                        2. Structure: Minimum 5 modules.
                        3. Lessons: 3-5 per module.
                        4. Language: Ukrainian ONLY.
                        5. Output: JSON only.
                        """
                    },
                    {"role": "user", "content": json.dumps({"topic": user_input})}
                ]
            )

            model_output = response.choices[0].message.content
            usage = response.usage

            # Просто зберігаємо статистику, нічого не списуємо
            chat_entry.model_response = model_output
            chat_entry.input_tokens = getattr(usage, "prompt_tokens", 0)
            chat_entry.output_tokens = getattr(usage, "completion_tokens", 0)
            chat_entry.total_tokens = getattr(usage, "total_tokens", 0)
            chat_entry.save()

            parsed = safe_json_parse(model_output)
            create_course_from_json(request.user, parsed)

            return Response(parsed, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"ERROR: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        courses = (
            CourseModel.objects
            .filter(owner=user)
            .prefetch_related("modules__lessons")
            .order_by('-created_at')
        )

        data = []
        for course in courses:
            course_data = {
                "id": course.id,
                "topic": course.topic,
                "modules": []
            }
            for module in course.modules.all():
                module_data = {
                    "id": module.id,
                    "title": module.title,
                    "lessons": [
                        {
                            "id": lesson.id,
                            "title": lesson.title,
                            "type": lesson.type
                        }
                        for lesson in module.lessons.all()
                    ]
                }
                course_data["modules"].append(module_data)
            data.append(course_data)

        return Response(data, status=status.HTTP_200_OK)


class GetCourseAPIView(APIView):
    # Цей клас ти не просив змінювати, але він і так не мав логіки токенів.
    # Залишаємо як було.
    def get(self, request, course_id=None):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        if course_id:
            course = (
                CourseModel.objects
                .filter(id=course_id, owner=user)
                .prefetch_related("modules__lessons")
                .first()
            )
            if not course:
                return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)
            
            result = {
                "id": course.id,
                "topic": course.topic,
                "modules": [
                    {
                        "id": m.id,
                        "title": m.title,
                        "lessons": [
                            {"id": l.id, "title": l.title, "type": l.type} 
                            for l in m.lessons.all()
                        ]
                    } for m in course.modules.all()
                ]
            }
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({"error": "ID required"}, status=status.HTTP_400_BAD_REQUEST)


class GenerateLessonAPIView(APIView):
    """
    GET /lessons/<lesson_id>/generate/
    Generates Markdown lesson.
    No economy checks.
    """

    def get(self, request, lesson_id: int):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Перевірка балансу видалена

        lesson = (
            LessonModel.objects
            .filter(id=lesson_id, module__course__owner=user)
            .select_related("module__course")
            .first()
        )

        if not lesson:
            return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)

        if lesson.content and len(lesson.content) > 10:
            return Response(lesson.content, status=status.HTTP_200_OK)

        payload = {
            "lesson_type": lesson.type,
            "lesson_title": lesson.title,
            "course_topic": lesson.module.course.topic
        }

        try:
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                temperature=0.7,
                max_tokens=4000, # Запобіжник від 402 помилки
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an expert educator. Generate a detailed lesson in Ukrainian using Markdown.
Structure:
- # Title
- ## Sections
- **Key terms**
- Code blocks (if IT related)
"""
                    },
                    {
                        "role": "user",
                        "content": json.dumps(payload, ensure_ascii=False)
                    }
                ]
            )

            md_output = response.choices[0].message.content
            
            # Ніякого списання токенів!
            
            lesson.content = md_output
            lesson.save()

            return Response(md_output, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            