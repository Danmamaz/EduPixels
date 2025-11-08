from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(models.Model):
    username = models.CharField(
        max_length=150,
        unique=True,
        
    )
    password = models.CharField(max_length=128)
    email = models.EmailField()
    date_joined = models.DateTimeField(default=timezone.now)
