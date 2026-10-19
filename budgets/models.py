from django.conf import settings
from django.db import models

from finance.models import Category


class Budget(models.Model):
    """Monthly spending limit for a category, in the user's base currency."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="budgets"
    )
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name="budget")
    monthly_limit = models.DecimalField(max_digits=14, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(monthly_limit__gt=0), name="budget_limit_positive"
            ),
        ]

    def __str__(self):
        return f"{self.category.name}: {self.monthly_limit}"


class BudgetThreshold(models.IntegerChoices):
    WARNING = 80, "80%"
    EXCEEDED = 100, "100%"


class BudgetNotification(models.Model):
    """Records a sent alert so each threshold is reported once per month."""

    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="notifications")
    month = models.DateField(help_text="First day of the month.")
    threshold = models.PositiveSmallIntegerField(choices=BudgetThreshold)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-month", "threshold"]
        constraints = [
            models.UniqueConstraint(
                fields=["budget", "month", "threshold"], name="unique_budget_notification"
            ),
        ]

    def __str__(self):
        return f"{self.budget} {self.month:%Y-%m} {self.threshold}%"
