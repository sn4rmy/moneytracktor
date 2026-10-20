from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class AccountType(models.TextChoices):
    CASH = "cash", "Cash"
    CARD = "card", "Card"
    DEPOSIT = "deposit", "Deposit"


class TransactionType(models.TextChoices):
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class Account(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=AccountType)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TransactionType)

    class Meta:
        ordering = ["type", "name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Transfer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transfers"
    )
    from_account = models.ForeignKey(
        Account, on_delete=models.RESTRICT, related_name="outgoing_transfers"
    )
    to_account = models.ForeignKey(
        Account, on_delete=models.RESTRICT, related_name="incoming_transfers"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    date = models.DateField()

    def __str__(self):
        return f"Transfer {self.date} {self.amount}"


class Transaction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions"
    )
    account = models.ForeignKey(Account, on_delete=models.RESTRICT, related_name="transactions")
    # Transactions created by a transfer have no category.
    category = models.ForeignKey(
        Category, on_delete=models.RESTRICT, null=True, blank=True, related_name="transactions"
    )
    transfer = models.ForeignKey(
        Transfer, on_delete=models.CASCADE, null=True, blank=True, related_name="transactions"
    )
    type = models.CharField(max_length=10, choices=TransactionType)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    date = models.DateField()
    note = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-date", "-id"]
        indexes = [models.Index(fields=["user", "date"], name="transaction_user_date_idx")]

    def __str__(self):
        return f"{self.date} {self.type} {self.amount}"
