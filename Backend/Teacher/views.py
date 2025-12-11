import os
from pathlib import Path
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
import json

from Courses.views import safe_json_parse
from Courses.models import *

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



class CheckHomeworkAPIView(APIView):
    """
    POST /modules/<module_id>/check_homework/
    Body: { "submission": "print('hello world')" }
    
    Зміни:
    Тепер ми приймаємо module_id, бо в модулі всього одна домашка.
    Менше ID-шників на фронті — менше головного болю.
    """

    def post(self, request, module_id):
        user = request.user
        request.user.update_streak()
        if not user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # === ЗМІНА ТУТ ===
        # Ми шукаємо домашку, яка прив'язана до конкретного модуля (module__id=module_id)
        # І перевіряємо власника через ланцюжок module -> course -> owner
        homework = HomeworkModel.objects.filter(
            module__id=module_id, 
            module__course__owner=user
        ).first()

        if not homework:
            # Це може статися, якщо модуль є, а кнопку "Згенерувати ДЗ" юзер ще не натиснув
            return Response(
                {"error": "Homework for this module not found. Generate it first."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        new_submission = request.data.get("submission", "").strip()
        if not new_submission:
            return Response({"error": "Submission is empty. Write some code."}, status=status.HTTP_400_BAD_REQUEST)

        # === Оптимізація/Кешування ===
        if homework.user_submission == new_submission and homework.grade is not None:
            return Response({
                "grade": homework.grade,
                "feedback": homework.ai_feedback,
                "status": "cached"
            }, status=status.HTTP_200_OK)

        # === AI Code Review ===
        payload = {
            "task_description": homework.content,
            "student_code": new_submission
        }

        try:
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",
                temperature=0.3,
                response_format={ "type": "json_object" },
                messages=[
                    {
                        "role": "system",
                        "content": """
You are a strict Senior Code Reviewer. 
Your goal is to grade the student's submission based strictly on the provided Task Description.

OUTPUT JSON FORMAT:
{
    "grade": 0-100 (integer),
    "feedback": "Detailed explanation in Ukrainian. Use Markdown. Criticize bad practices, praise good ones. Be constructive but professional."
}

CRITERIA:
1. If code does not work or misses the point -> Low score (<50).
2. If logic is correct but style is bad -> Medium score (50-80).
3. If clean and correct -> High score (80-100).
4. Language: Ukrainian.
"""
                    },
                    {
                        "role": "user",
                        "content": json.dumps(payload, ensure_ascii=False)
                    }
                ]
            )

            ai_raw = response.choices[0].message.content
            parsed_feedback = safe_json_parse(ai_raw)

            homework.user_submission = new_submission
            homework.grade = parsed_feedback.get("grade", 0)
            homework.ai_feedback = parsed_feedback.get("feedback", "No feedback generated.")
            
            homework.save()

            return Response({
                "grade": homework.grade,
                "feedback": homework.ai_feedback,
                "status": "fresh"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": f"AI Check failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)