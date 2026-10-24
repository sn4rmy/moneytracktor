import pytest
from django.urls import reverse

from finance.models import Category
from tests.factories import CategoryFactory, TransactionFactory

pytestmark = pytest.mark.django_db


def test_list_returns_only_own_categories(auth_client, user):
    own = CategoryFactory(user=user)
    CategoryFactory()

    response = auth_client.get(reverse("category-list"))

    assert response.status_code == 200
    assert [category["id"] for category in response.data] == [own.id]


def test_create_category(auth_client, user):
    response = auth_client.post(reverse("category-list"), {"name": "Books", "type": "expense"})

    assert response.status_code == 201
    assert response.data["name"] == "Books"
    assert Category.objects.get(id=response.data["id"]).user == user


def test_rename_category(auth_client, user):
    category = CategoryFactory(user=user, name="Food")

    response = auth_client.patch(reverse("category-detail", args=[category.id]), {"name": "Meals"})

    assert response.status_code == 200
    category.refresh_from_db()
    assert category.name == "Meals"


def test_change_category_type_returns_400(auth_client, user):
    category = CategoryFactory(user=user, type="expense")

    response = auth_client.patch(reverse("category-detail", args=[category.id]), {"type": "income"})

    assert response.status_code == 400
    assert "type" in response.data


def test_delete_category(auth_client, user):
    category = CategoryFactory(user=user)

    response = auth_client.delete(reverse("category-detail", args=[category.id]))

    assert response.status_code == 204
    assert not Category.objects.filter(id=category.id).exists()


def test_delete_category_with_transactions_returns_400(auth_client, user):
    transaction = TransactionFactory(user=user)

    response = auth_client.delete(reverse("category-detail", args=[transaction.category.id]))

    assert response.status_code == 400
    assert response.data["detail"] == "Cannot delete a category that has transactions."
    assert Category.objects.filter(id=transaction.category.id).exists()


def test_other_users_category_returns_404(auth_client):
    category = CategoryFactory()

    response = auth_client.delete(reverse("category-detail", args=[category.id]))

    assert response.status_code == 404
    assert Category.objects.filter(id=category.id).exists()


def test_categories_without_token_return_401(api_client):
    response = api_client.get(reverse("category-list"))

    assert response.status_code == 401
