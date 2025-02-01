from django.test import TestCase
import pytest
from django.urls import reverse
from django.core import mail
from django.contrib.auth.models import User
from account.models import AccountStatus 
from pentagon.settings import SITE_URL
# Create your tests here.

@pytest.mark.django_db
def test_sign_up(client, settings):
    """Test user registration and email verification."""
    
    # Mock site URL for verification link
    settings.SITE_URL = "http://127.0.0.1:8000/"
    
    # Form data for user creation
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password1": "StrongPassword123!",
        "password2": "StrongPassword123!"
    }
    
    # Send POST request to sign-up endpoint
    response = client.post(reverse('sign_up'), user_data)

    # Check if user is created in the database
    assert User.objects.filter(username="testuser").exists()

    # Check if AccountStatus object is created
    user = User.objects.get(username="testuser")
    assert AccountStatus.objects.filter(user=user).exists()

    # Check if the email was sent
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Welcome To Pentagon"
    assert user.email in mail.outbox[0].to
    assert "verify_email" in mail.outbox[0].body  # Ensure the email contains the verification link

    # Ensure the response redirects to sign-in page
    assert response.status_code == 302  # HTTP 302 = Redirect
    assert response.url == reverse('sign-in')
