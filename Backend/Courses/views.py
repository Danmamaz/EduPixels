from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import CoursePromptSerializer
import requests
import os
import httpx
from dotenv import load_dotenv
import json


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class GenerateCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"detail": "Missing prompt"}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": (
                    "You generate a structured course outline. "
                    "Return only JSON in this exact format: "
                    "[{\"chapter_title\": string, \"topics\": [{\"topic_title\": string}]}]"
                )},
                {"role": "user", "content": prompt}
            ]
        }

        try:
            r = requests.post(url, json=payload, headers=headers, timeout=30)
            data = r.json()

            # DEBUG: return error message from OpenRouter
            if "error" in data:
                return Response({"detail": data["error"]}, status=500)

            # If no choices field → API error
            if "choices" not in data:
                return Response({"detail": "OpenRouter returned invalid response", "raw": data}, status=500)

            content = data["choices"][0]["message"]["content"]

            # Parse JSON from model response
            course_json = json.loads(content)

            return Response(course_json, status=200)

        except Exception as e:
            return Response({"detail": str(e)}, status=500)