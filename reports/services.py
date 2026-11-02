from django.db.models import Q, Sum
from django.db.models.functions import ExtractMonth

from finance.models import Transaction, TransactionType


def get_report_transactions(user):
    # Transfers only move money between own accounts, so they are not income or expenses.
    return Transaction.objects.filter(user=user, transfer__isnull=True)


def get_summary(user, date_from, date_to):
    income = Sum("amount", filter=Q(type=TransactionType.INCOME), default=0)
    expense = Sum("amount", filter=Q(type=TransactionType.EXPENSE), default=0)
    transactions = get_report_transactions(user).filter(date__range=(date_from, date_to))
    return transactions.aggregate(income=income, expense=expense, total=income - expense)


def get_expenses_by_category(user, date_from, date_to):
    expenses = get_report_transactions(user).filter(
        type=TransactionType.EXPENSE, date__range=(date_from, date_to)
    )
    return (
        expenses.values("category", "category__name")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )


def get_monthly_report(user, year):
    income = Sum("amount", filter=Q(type=TransactionType.INCOME), default=0)
    expense = Sum("amount", filter=Q(type=TransactionType.EXPENSE), default=0)
    transactions = get_report_transactions(user).filter(date__year=year)
    return (
        transactions.annotate(month=ExtractMonth("date"))
        .values("month")
        .annotate(income=income, expense=expense)
        .order_by("month")
    )
