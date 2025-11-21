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
    raise ValueError("OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file.")

# Create OpenRouter client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)


def safe_json_parse(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            cleaned = text[start:end]
            return json.loads(cleaned)
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
    POST endpoint to generate a course and save token usage.
    GET endpoint returns all user courses without lesson content.
    """

    def post(self, request):
        user_input = request.data.get("prompt")
        if not user_input:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        chat_entry = ChatPrompt.objects.create(user_input=user_input)

        try:
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": """
                        You are a high-level curriculum design AI specialized in IT topics. Your task is to create a detailed, logically structured course based on a user-provided topic. The course must cover content from beginner fundamentals to professional-level mastery. The output must be in Ukrainian.  

                        -------------------------------------
                        INPUT FORMAT (JSON):
                        {
                        "topic": "string"
                        }

                        -------------------------------------
                        OUTPUT FORMAT (strict JSON, Ukrainian only):
                        {
                        "meta": {
                            "topic": string
                        },
                        "modules": [
                            {
                            "title": string,
                            "lessons": [
                                {
                                "title": string,
                                "type": "lecture"
                                }
                            ]
                            }
                        ]
                        }

                        -------------------------------------
                        RULES:
                        1. The course topic must relate ONLY to IT. If a non-IT topic is given, adapt it to an IT-related version.
                        2. Course level is always beginner.
                        3. Course goal is always: "Опановувати тему до професійного рівня".
                        4. Modules must be logically ordered from basics to professional practice.
                        5. Minimum 10 modules, each with at least 5 lessons.
                        6. Each lesson must include: type="lecture", title.
                        7. Do NOT include unrelated frameworks, certifications, or materials.
                        8. Do NOT include durations, audience, constraints, or total duration fields.
                        9. All module and lesson titles must be concise, professional, and measurable.
                        10. Output must be valid JSON; do not include comments or explanations outside JSON.

                        -------------------------------------
                        TASK:
                        Generate a full professional-level IT course in Ukrainian according to these rules when provided with the input JSON.

                        """
                    },
                    {"role": "user", "content": user_input}
                ]
            )

            model_output = response.choices[0].message.content
            usage = response.usage

            # Save token usage BEFORE JSON parsing
            chat_entry.model_response = model_output
            chat_entry.input_tokens = getattr(usage, "prompt_tokens", 0)
            chat_entry.output_tokens = getattr(usage, "completion_tokens", 0)
            chat_entry.total_tokens = getattr(usage, "total_tokens", 0)
            chat_entry.save()

            parsed = safe_json_parse(model_output)
            create_course_from_json(request.user, parsed)

            return Response(parsed, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        courses = (
            CourseModel.objects
            .filter(owner=user)
            .prefetch_related("modules__lessons")
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
                            # NOTE: content is NOT included
                        }
                        for lesson in module.lessons.all()
                    ]
                }
                course_data["modules"].append(module_data)
            data.append(course_data)

        return Response(data, status=status.HTTP_200_OK)


class GetCourseAPIView(APIView):
    """
    GET endpoint to return a single course by ID (without lesson content)
    """

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
            courses = [course]
        else:
            # Return all courses if no ID
            courses = CourseModel.objects.filter(owner=user).prefetch_related("modules__lessons")

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
                            # content is excluded
                        }
                        for lesson in module.lessons.all()
                    ]
                }
                course_data["modules"].append(module_data)
            data.append(course_data)

        # If single course_id requested, return object instead of list
        return Response(data[0] if course_id else data, status=status.HTTP_200_OK)


class GenerateLessonAPIView(APIView):
    """
    GET /lessons/<lesson_id>/generate/
    Generates (or returns cached) Markdown lesson.
    Saves generated Markdown into lesson.content.
    """

    def get(self, request, lesson_id: int):
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        lesson = (
            LessonModel.objects
            .filter(id=lesson_id, module__course__owner=user)
            .select_related("module__course")
            .first()
        )

        if not lesson:
            return Response({"error": "Lesson not found"}, status=status.HTTP_404_NOT_FOUND)

        # ----------------------------------------------------
        # 1. CONTENT ALREADY EXISTS → RETURN CACHED VERSION
        # ----------------------------------------------------
        if lesson.content and lesson.content.strip() != "[]":
            return Response(
                lesson.content,
                status=status.HTTP_200_OK
            )

        # ----------------------------------------------------
        # 2. GENERATE CONTENT
        # ----------------------------------------------------
        payload = {
            "lesson_type": lesson.type,
            "lesson_title": lesson.title
        }

        try:
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                temperature=0.7,
                messages=[
                    {
                        "role": "system",
                        "content": """
You are an expert educator and curriculum designer. Your task is to generate a detailed lesson based only on the provided lesson type and lesson title. Follow these rules strictly:

1. Output must be entirely in Ukrainian.
2. Use Markdown formatting:
   - # for main lesson title
   - ## for major sections
   - ### for sub-sections
   - Use **bold** for key terms and concepts.
   - Use bullet points or numbered lists for examples, exercises, or steps.
3. Each lesson should include:
   - Introduction
   - Main Content (clear sections)
   - Examples or exercises
   - Summary / Key takeaways
4. Focus on clarity for beginner → intermediate learners.

Input example:
{
  "lesson_type": "Теоретичний",
  "lesson_title": "Основи об’єктно-орієнтованого програмування"
}

Output: Markdown lesson in Ukrainian.
"""
                    },
                    {
                        "role": "user",
                        "content": json.dumps(payload, ensure_ascii=False)
                    }
                ]
            )

            md_output = response.choices[0].message.content

            # ----------------------------------------------------
            # 3. SAVE TO DB
            # ----------------------------------------------------
            lesson.content = md_output
            lesson.save()

            return Response(
                    md_output,
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
