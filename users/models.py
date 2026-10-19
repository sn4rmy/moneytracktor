from django.contrib.auth.models import AbstractUser
from django.db import models

from core.currency import Currency


class User(AbstractUser):
    email = models.EmailField(unique=True)
    base_currency = models.CharField(max_length=3, choices=Currency, default=Currency.KZT)
