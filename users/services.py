from django.db import transaction

from finance.models import Category, TransactionType

from .models import User

DEFAULT_CATEGORIES = [
    ("Food", TransactionType.EXPENSE),
    ("Transport", TransactionType.EXPENSE),
    ("Housing", TransactionType.EXPENSE),
    ("Entertainment", TransactionType.EXPENSE),
    ("Scholarship", TransactionType.INCOME),
    ("Salary", TransactionType.INCOME),
    ("Gifts", TransactionType.INCOME),
]


@transaction.atomic
def register_user(username, email, password):
    user = User.objects.create_user(username=username, email=email, password=password)
    categories = [
        Category(user=user, name=name, type=category_type)
        for name, category_type in DEFAULT_CATEGORIES
    ]
    Category.objects.bulk_create(categories)
    return user
