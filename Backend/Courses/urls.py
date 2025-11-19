# courses/urls.py
from django.urls import path
from .views import GenerateCourseView

urlpatterns = [
    path('', GenerateCourseView.as_view(), name='generate_course'),
]
