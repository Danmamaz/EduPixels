from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class CustomUser(models.Model):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password, hashed=False):
        """hashed=True if password comes SHA256 from client"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password, hashed=False):
        """hashed=True if password comes SHA256 from client"""
        return check_password(raw_password, self.password)

    @property
    def is_authenticated(self):
        return True  # always True for logged-in users

    @property
    def is_active(self):
        return True  # treat all users as active

    def __str__(self):
        return self.username


class TokenTransaction(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='token_transactions')
    input_token = models.IntegerField(default=0)
    output_token = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transaction {self.id} for {self.user.username}: +{self.input_token} -{self.output_token} at {self.date}"