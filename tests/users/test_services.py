import pytest

from users.services import register_user

pytestmark = pytest.mark.django_db


def test_register_user_hashes_password():
    user = register_user(username="alice", email="alice@example.com", password="Str0ng-pass-42")

    assert user.password != "Str0ng-pass-42"
    assert user.check_password("Str0ng-pass-42")


def test_register_user_creates_default_categories():
    user = register_user(username="alice", email="alice@example.com", password="Str0ng-pass-42")

    assert set(user.categories.values_list("name", "type")) == {
        ("Food", "expense"),
        ("Transport", "expense"),
        ("Housing", "expense"),
        ("Entertainment", "expense"),
        ("Scholarship", "income"),
        ("Salary", "income"),
        ("Gifts", "income"),
    }
