import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.mark.django_db
def test_signup_success(api_client):
    url = reverse('signup') 
    payload = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "strongpassword123"
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["username"] == "testuser"

@pytest.mark.django_db
def test_login_success(api_client):
    user = User.objects.create_user(username="loginuser", email="login@example.com", password="loginpass123")
    url = reverse('login') 
    payload = {
        "username": "loginuser",
        "password": "loginpass123"
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.data


@pytest.mark.django_db
def test_jwt_auth_protected_view(api_client):
    user = User.objects.create_user(username="jwtuser", email="jwt@example.com", password="jwtpass123")
    login_url = reverse('login')
    payload = {
        "username": "jwtuser",
        "password": "jwtpass123"
    }
    response = api_client.post(login_url, payload, format='json')
    token = response.data["token"]

    # 보호된 API 요청
    protected_url = reverse('protected')
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    protected_response = api_client.get(protected_url)

    assert protected_response.status_code == status.HTTP_200_OK
    assert protected_response.data["detail"] == "You are authenticated!"

