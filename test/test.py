import pytest
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

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

    response2 = api_client.post(url, payload, format='json')
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert response2.data['error']['code'] == "USER_ALREADY_EXISTS"

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
    
    payload2 = {
        "username": "loginuser",
        "password": "loginpass12"
    }
    response = api_client.post(url, payload2, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['error']['code']=="INVALID_CREDENTIALS"

def generate_valid_token(user):
    access_token = AccessToken.for_user(user)
    return str(access_token)

def generate_expired_token(user):
    access_token = AccessToken.for_user(user)
    access_token.set_exp(lifetime=timedelta(seconds=-1))
    return str(access_token)


@pytest.mark.django_db
def test_token_not_found(api_client):
    user = User.objects.create_user(username="loginuser", email="login@example.com", password="loginpass123")
    url = reverse('protected')

    #토큰이 없는 경우
    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["error"]["message"] == "토큰이 없습니다."

    #정상적인 경우
    token = generate_valid_token(user)    
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["message"] == "토큰이 인증 되었습니다."
 
    