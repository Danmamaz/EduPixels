from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    username = models.CharField(max_length=25, unique=True)
    email = models.EmailField(unique=True)

    streak_days = models.IntegerField(default=0, help_text="Кількість днів поспіль")
    last_submission_date = models.DateField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = 'custom_user'

    # Метод, який ти будеш викликати при успішній здачі ДЗ
    def update_streak(self):
        today = timezone.now().date()
        
        # Якщо юзер вже щось здавав сьогодні — не чіпаємо, не накручуємо
        if self.last_submission_date == today:
            return

        # Якщо остання здача була вчора — інкрементуємо (дофамін пішов!)
        if self.last_submission_date == today - timedelta(days=1):
            self.streak_days += 1
        else:
            # Юзер пропустив день або це перша здача — скидаємо на 1
            self.streak_days = 1
            
        self.last_submission_date = today
        self.save()

    @property
    def is_on_fire(self):
        # Вогник даємо, якщо стрік 2 дні або більше
        return self.streak_days >= 2

    class Meta:
        db_table = 'custom_user'