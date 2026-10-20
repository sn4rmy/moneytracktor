from decimal import Decimal

import factory
from django.utils import timezone

from budgets.models import Budget
from finance.models import Account, AccountType, Category, Transaction, TransactionType, Transfer
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.django.Password("password123")


class AccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Account

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Account {n}")
    type = AccountType.CARD


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Category {n}")
    type = TransactionType.EXPENSE


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    # The account and the category belong to the same user as the transaction.
    account = factory.SubFactory(AccountFactory, user=factory.SelfAttribute("..user"))
    category = factory.SubFactory(CategoryFactory, user=factory.SelfAttribute("..user"))
    type = TransactionType.EXPENSE
    amount = Decimal("1500.00")
    date = factory.LazyFunction(timezone.localdate)


class TransferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transfer

    user = factory.SubFactory(UserFactory)
    from_account = factory.SubFactory(AccountFactory, user=factory.SelfAttribute("..user"))
    to_account = factory.SubFactory(AccountFactory, user=factory.SelfAttribute("..user"))
    amount = Decimal("5000.00")
    date = factory.LazyFunction(timezone.localdate)


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory, user=factory.SelfAttribute("..user"))
    monthly_limit = Decimal("100000.00")
