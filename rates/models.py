from django.db import models

from core.currency import Currency


class ExchangeRate(models.Model):
    """Price of one unit of a currency in KZT on a given date."""

    currency = models.CharField(max_length=3, choices=Currency)
    date = models.DateField()
    rate = models.DecimalField(max_digits=12, decimal_places=4)

    class Meta:
        ordering = ["-date", "currency"]
        constraints = [
            models.UniqueConstraint(
                fields=["currency", "date"], name="unique_rate_per_currency_date"
            ),
            models.CheckConstraint(condition=models.Q(rate__gt=0), name="exchange_rate_positive"),
        ]

    def __str__(self):
        return f"{self.currency} {self.date}: {self.rate}"
