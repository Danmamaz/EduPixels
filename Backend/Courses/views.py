import os
from pathlib import Path
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
import json
from .models import *
from django.db import transaction


from .models import ChatPrompt
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

class ChatAPIView(APIView):
    """
    POST endpoint to send a prompt to OpenRouter and return a response
    with token usage tracked.
    """

    def post(self, request):
        user_input = request.data.get("prompt")
        if not user_input:
            return Response({"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Save prompt in DB
        chat_entry = ChatPrompt.objects.create(user_input=user_input)

        try:
            # Send prompt to OpenRouter
            response = client.chat.completions.create(
                model="openai/gpt-3.5-turbo",
                temperature=0.7,
                messages=[
                    {"role": "system", "content": """
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
                        6. Each lesson must include: type="lecture", title, and resources.
                        7. Do NOT include unrelated frameworks, certifications, or materials.
                        8. Do NOT include durations, audience, constraints, or total duration fields.
                        9. All module and lesson titles must be concise, professional, and measurable.
                        10. Output must be valid JSON; do not include comments or explanations outside JSON.

                        -------------------------------------
                        TASK:
                        Generate a full professional-level IT course in Ukrainian according to these rules when provided with the input JSON.

                    """},
                    {"role": "user", "content": user_input}
                ]
            )

            # Extract model response and usage
            model_output = response.choices[0].message.content
            usage = response.usage  # contains prompt_tokens, completion_tokens, total_tokens

            parsed = json.loads(model_output)
            course = create_course_from_json(request.user, parsed)

            # Save response and usage in DB
            chat_entry.model_response = model_output
            chat_entry.input_tokens = usage.prompt_tokens
            chat_entry.output_tokens = usage.completion_tokens
            chat_entry.total_tokens = usage.total_tokens

            chat_entry.save()

            serializer = ChatPromptSerializer(chat_entry)
            return Response(json.loads(model_output), status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
def create_course_from_json(user, course_json):

            if not user or not user.is_authenticated:
                raise ValueError("User must be authenticated")

            if isinstance(course_json, str):
                course_json = json.loads(course_json)

            topic = course_json["meta"]["topic"]
            modules_data = course_json["modules"]

            # Ensure DB consistency
            with transaction.atomic():

                # Create Course
                course = CourseModel.objects.create(
                    topic=topic,
                    owner=user
                )

                # Create Modules and Lessons
                for module_data in modules_data:
                    module = ModuleModel.objects.create(
                        title=module_data["title"]
                    )

                    for lesson_data in module_data["lessons"]:
                        lesson = LessonModel.objects.create(
                            title=lesson_data["title"],
                            type=lesson_data["type"],
                            content=json.dumps(lesson_data.get("resources", []))
                        )
                        module.lessons.add(lesson)

                    course.modules.add(module)

                course.save()

            return course