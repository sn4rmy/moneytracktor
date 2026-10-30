from django.db import transaction
from django.db.models import Q, Sum
from rest_framework.exceptions import ValidationError

from .models import Account, Transaction, TransactionType, Transfer


def get_accounts_with_balance(user):
    income = Sum(
        "transactions__amount",
        filter=Q(transactions__type=TransactionType.INCOME),
        default=0,
    )
    expense = Sum(
        "transactions__amount",
        filter=Q(transactions__type=TransactionType.EXPENSE),
        default=0,
    )
    accounts = Account.objects.filter(user=user).annotate(balance=income - expense)
    # Meta.ordering is ignored in queries with GROUP BY, so the order is set here.
    return accounts.order_by("name")


@transaction.atomic
def create_transfer(user, from_account, to_account, amount, date):
    transfer = Transfer.objects.create(
        user=user,
        from_account=from_account,
        to_account=to_account,
        amount=amount,
        date=date,
    )
    Transaction.objects.create(
        user=user,
        account=from_account,
        transfer=transfer,
        type=TransactionType.EXPENSE,
        amount=amount,
        date=date,
        note=f"Transfer to {to_account.name}",
    )
    Transaction.objects.create(
        user=user,
        account=to_account,
        transfer=transfer,
        type=TransactionType.INCOME,
        amount=amount,
        date=date,
        note=f"Transfer from {from_account.name}",
    )
    return transfer


def delete_account(account):
    if account.transactions.exists():
        raise ValidationError({"detail": "Cannot delete an account that has transactions."})
    account.delete()


def delete_category(category):
    if category.transactions.exists():
        raise ValidationError({"detail": "Cannot delete a category that has transactions."})
    category.delete()


def delete_transaction(instance):
    if instance.transfer_id is not None:
        raise ValidationError({"detail": "Transactions created by a transfer cannot be deleted."})
    instance.delete()
