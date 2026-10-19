from django.db import models


class Currency(models.TextChoices):
    KZT = "KZT", "Kazakhstani tenge"
    USD = "USD", "US dollar"
    EUR = "EUR", "Euro"
    RUB = "RUB", "Russian ruble"
