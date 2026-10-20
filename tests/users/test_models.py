import pytest
from django.db import IntegrityError

from tests.factories import UserFactory

pytestmark = pytest.mark.django_db


def test_email_must_be_unique():
    UserFactory(email="same@example.com")

    with pytest.raises(IntegrityError):
        UserFactory(email="same@example.com")
