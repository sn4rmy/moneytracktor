from datetime import date
from decimal import Decimal

import pytest
from django.urls import reverse

from tests.factories import CategoryFactory, TransactionFactory

pytestmark = pytest.mark.django_db

PERIOD = {"date_from": "2026-10-01", "date_to": "2026-10-31"}


def test_summary_report(auth_client, user):
    TransactionFactory(
        user=user,
        type="income",
        category__type="income",
        amount=Decimal("250000.00"),
        date=date(2026, 10, 10),
    )
    TransactionFactory(user=user, amount=Decimal("2500.50"), date=date(2026, 10, 12))

    response = auth_client.get(reverse("report-summary"), PERIOD)

    assert response.status_code == 200
    assert response.data == {"income": "250000.00", "expense": "2500.50", "total": "247499.50"}


def test_summary_report_without_dates_returns_400(auth_client):
    response = auth_client.get(reverse("report-summary"))

    assert response.status_code == 400
    assert "date_from" in response.data
    assert "date_to" in response.data


def test_summary_report_shows_only_own_transactions(auth_client, user):
    TransactionFactory(user=user, amount=Decimal("1000.00"), date=date(2026, 10, 5))
    TransactionFactory(amount=Decimal("7000.00"), date=date(2026, 10, 5))

    response = auth_client.get(reverse("report-summary"), PERIOD)

    assert response.data["expense"] == "1000.00"


def test_by_category_report(auth_client, user):
    food = CategoryFactory(user=user, name="Food", type="expense")
    TransactionFactory(user=user, category=food, amount=Decimal("2000.00"), date=date(2026, 10, 5))

    response = auth_client.get(reverse("report-by-category"), PERIOD)

    assert response.status_code == 200
    assert response.data == [{"category": food.id, "category_name": "Food", "total": "2000.00"}]


def test_monthly_report(auth_client, user):
    TransactionFactory(user=user, amount=Decimal("5000.00"), date=date(2026, 3, 5))

    response = auth_client.get(reverse("report-monthly"), {"year": 2026})

    assert response.status_code == 200
    assert response.data == [{"month": 3, "income": "0.00", "expense": "5000.00"}]


@pytest.mark.parametrize("params", [{}, {"year": "0"}])
def test_monthly_report_with_invalid_year_returns_400(auth_client, params):
    response = auth_client.get(reverse("report-monthly"), params)

    assert response.status_code == 400
    assert "year" in response.data


@pytest.mark.parametrize("url_name", ["report-summary", "report-by-category", "report-monthly"])
def test_report_without_token_returns_401(api_client, url_name):
    response = api_client.get(reverse(url_name))

    assert response.status_code == 401
