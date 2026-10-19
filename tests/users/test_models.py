import pytest
from django.db import IntegrityError

from core.currency import Currency
from tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_base_currency_defaults_to_kzt():
    user = UserFactory()

    assert user.base_currency == Currency.KZT


def test_email_must_be_unique():
    UserFactory(email="same@example.com")

    with pytest.raises(IntegrityError):
        UserFactory(email="same@example.com")
