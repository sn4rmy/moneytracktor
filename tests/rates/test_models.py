import datetime
from decimal import Decimal

import pytest
from django.db import IntegrityError, transaction

from tests.factories import ExchangeRateFactory

pytestmark = pytest.mark.django_db


def test_one_rate_per_currency_and_date():
    day = datetime.date(2026, 3, 1)
    ExchangeRateFactory(currency="USD", date=day)
    ExchangeRateFactory(currency="EUR", date=day)

    with pytest.raises(IntegrityError), transaction.atomic():
        ExchangeRateFactory(currency="USD", date=day)


def test_rate_must_be_positive():
    with pytest.raises(IntegrityError), transaction.atomic():
        ExchangeRateFactory(rate=Decimal("0"))
