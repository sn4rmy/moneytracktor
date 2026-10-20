from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from finance.models import Category


class Budget(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets"
    )
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name="budget")
    monthly_limit = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    # First day of the month for which the over-limit email was already sent.
    last_alert_month = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.category}: {self.monthly_limit}"
