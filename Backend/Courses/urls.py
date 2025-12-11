# courses/urls.py
from django.urls import path
from .views import ChatAPIView, GetCourseAPIView, GenerateLessonAPIView, GenerateHomeworkAPIView

urlpatterns = [
    path('', ChatAPIView.as_view(), name='generate_course'),
    path('<int:course_id>/', GetCourseAPIView.as_view()),
    path("lessons/<int:lesson_id>/", GenerateLessonAPIView.as_view()),
    path("modules/<module_id>/generate_homework/", GenerateHomeworkAPIView.as_view()),
    

]
