from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

class TestModels(TestCase):
    def setUp(self):
        self.testUser = User.objects.create(
            username = "TestUserForTokenGeneration",
            email = "testuser@tokenGen.com",
            password = "HelloWorld123@123"
        )

    def test_token_generation(self):
        token = Token.objects.get(user = self.testUser)

        self.assertIsNot(token, None)