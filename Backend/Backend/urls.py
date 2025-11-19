# project/urls.py
from django.contrib import admin
from django.urls import path, include
from Auth.views import ProfileView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('Auth.urls')),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('courses/', include('Courses.urls')),
]
