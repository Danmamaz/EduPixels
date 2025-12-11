from django.urls import path
from .views import CheckHomeworkAPIView

urlpatterns = [
    path("homeworks/<int:module_id>/check/", CheckHomeworkAPIView.as_view()),
]
