from django.conf import settings
from django.db import models
from django.db.models import Q

from core.currency import Currency


class AccountType(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    DEPOSIT = "deposit", "Deposit"


class CategoryType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class TransactionType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"
    TRANSFER_IN = "transfer_in", "Transfer in"
    TRANSFER_OUT = "transfer_out", "Transfer out"


class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=AccountType)
    currency = models.CharField(max_length=3, choices=Currency, default=Currency.KZT)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_account_name_per_user"),
        ]

    def __str__(self):
        return f"{self.name} ({self.currency})"


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CategoryType)

    class Meta:
        ordering = ["type", "name"]
        verbose_name_plural = "categories"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name", "type"], name="unique_category_name_per_user_and_type"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.type})"


class Transfer(models.Model):
    """Groups the two transactions of a move between the user's own accounts."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transfers"
    )
    # Units of the target account currency per one unit of the source account currency.
    rate = models.DecimalField(max_digits=18, decimal_places=8)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transfer #{self.pk}"


class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name="transactions")
    category = models.ForeignKey(
        Category,
        on_delete=models.RESTRICT,
        related_name="transactions",
        null=True,
        blank=True,
    )
    transfer = models.ForeignKey(
        Transfer,
        on_delete=models.CASCADE,
        related_name="transactions",
        null=True,
        blank=True,
    )
    type = models.CharField(max_length=12, choices=TransactionType)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["user", "date"], name="transaction_user_date_idx"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(amount__gt=0), name="transaction_amount_positive"),
            # Income and expense need a category; transfer parts need a transfer and no category.
            models.CheckConstraint(
                condition=(
                    Q(
                        type__in=[TransactionType.INCOME, TransactionType.EXPENSE],
                        category__isnull=False,
                        transfer__isnull=True,
                    )
                    | Q(
                        type__in=[TransactionType.TRANSFER_IN, TransactionType.TRANSFER_OUT],
                        category__isnull=True,
                        transfer__isnull=False,
                    )
                ),
                name="transaction_category_or_transfer",
            ),
        ]

    def __str__(self):
        return f"{self.date} {self.type} {self.amount}"
