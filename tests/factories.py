import datetime
from decimal import Decimal

import factory
from django.utils import timezone

from budgets.models import Budget, BudgetNotification, BudgetThreshold
from finance.models import (
    Account,
    AccountType,
    Category,
    CategoryType,
    Transaction,
    TransactionType,
    Transfer,
)
from imports.models import TransactionImport
from rates.models import ExchangeRate
from users.models import User


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

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
    type = CategoryType.EXPENSE


class TransferFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transfer

    user = factory.SubFactory(UserFactory)
    rate = Decimal("1")


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    account = factory.SubFactory(AccountFactory, user=factory.SelfAttribute("..user"))
    category = factory.SubFactory(CategoryFactory, user=factory.SelfAttribute("..user"))
    type = TransactionType.EXPENSE
    amount = Decimal("1500.00")
    date = factory.LazyFunction(timezone.localdate)


class ExchangeRateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExchangeRate

    currency = "USD"
    date = factory.Sequence(lambda n: datetime.date(2026, 1, 1) + datetime.timedelta(days=n))
    rate = Decimal("505.2500")


class BudgetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Budget

    user = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory, user=factory.SelfAttribute("..user"))
    monthly_limit = Decimal("100000.00")


class BudgetNotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BudgetNotification

    budget = factory.SubFactory(BudgetFactory)
    month = datetime.date(2026, 1, 1)
    threshold = BudgetThreshold.WARNING


class TransactionImportFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TransactionImport

    user = factory.SubFactory(UserFactory)
    file = factory.django.FileField(filename="transactions.csv", data=b"date,amount\n")
