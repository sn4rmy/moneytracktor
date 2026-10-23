import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from tests.factories import UserFactory
from users.models import User

pytestmark = pytest.mark.django_db


def test_register_creates_user(api_client):
    data = {"username": "alice", "email": "alice@example.com", "password": "Str0ng-pass-42"}

    response = api_client.post(reverse("register"), data)

    assert response.status_code == 201
    assert response.data["username"] == "alice"
    assert response.data["email"] == "alice@example.com"
    assert "password" not in response.data
    assert User.objects.filter(username="alice").exists()


def test_register_with_taken_email_returns_400(api_client):
    UserFactory(email="alice@example.com")
    data = {"username": "alice", "email": "alice@example.com", "password": "Str0ng-pass-42"}

    response = api_client.post(reverse("register"), data)

    assert response.status_code == 400
    assert "email" in response.data


def test_register_with_weak_password_returns_400(api_client):
    data = {"username": "alice", "email": "alice@example.com", "password": "12345"}

    response = api_client.post(reverse("register"), data)

    assert response.status_code == 400
    assert "password" in response.data


def test_login_returns_tokens(api_client):
    UserFactory(username="alice", password="Str0ng-pass-42")

    response = api_client.post(
        reverse("token-obtain"), {"username": "alice", "password": "Str0ng-pass-42"}
    )

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


def test_login_with_wrong_password_returns_401(api_client):
    UserFactory(username="alice", password="Str0ng-pass-42")

    response = api_client.post(
        reverse("token-obtain"), {"username": "alice", "password": "wrong-password"}
    )

    assert response.status_code == 401


def test_refresh_returns_new_access_token(api_client):
    refresh = RefreshToken.for_user(UserFactory())

    response = api_client.post(reverse("token-refresh"), {"refresh": str(refresh)})

    assert response.status_code == 200
    assert "access" in response.data


def test_me_returns_current_user(api_client):
    user = UserFactory()
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user)}")

    response = api_client.get(reverse("me"))

    assert response.status_code == 200
    assert response.data == {"id": user.id, "username": user.username, "email": user.email}


def test_me_without_token_returns_401(api_client):
    response = api_client.get(reverse("me"))

    assert response.status_code == 401
