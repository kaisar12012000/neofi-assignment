from django.test import TestCase, Client
from django.urls import reverse
from api.views import create_notes_view, get_update_notes_by_id_view, share_notes_view, get_version_history
from api.models import Notes, NotesVersion
from django.contrib.auth.models import User
import json
from rest_framework.authtoken.models import Token
from datetime import datetime
from uuid import uuid4

TEST_USERNAME_0 = "UnitTestUser0"
TEST_USER_0_EMAIL = "unit_test_user_0@testing.com"
TEST_USER_0_PASSWORD = "0000AAA@123"
TEST_USERNAME_1 = "UnitTestUser1"
TEST_USER_1_EMAIL = "unit_test_user_1@testing.com"
TEST_USER_1_PASSWORD = "A@123"
TEST_USERNAME_2 = "UnitTestUser2"
TEST_USER_2_EMAIL = "unit_test_user_2@testing.com"
TEST_USER_2_PASSWORD = "124@B"
TEST_NOTEID = uuid4()
TEST_NOTE_CONTENT = "This is dummy test note content"
TEST_NOTE_TITLE = "This is dummy test note title"
TEST_VERSIONID = uuid4()


class TestAuthViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.signup = reverse('signup')
        self.login = reverse('login')

        user = User.objects.create(username=TEST_USERNAME_0, email = TEST_USER_0_EMAIL, password = TEST_USER_0_PASSWORD)
        self.user_0_token = Token.objects.get(user = user)
        

    def test_signup_user_POST(self):
        
        response = self.client.post(self.signup, {
            "username": TEST_USERNAME_1,
            "email":TEST_USER_1_EMAIL,
            "password": TEST_USER_1_PASSWORD,
            "password2": TEST_USER_1_PASSWORD
        })

        self.assertEquals(response.status_code, 200)
        self.assertDictContainsSubset({
            "response": "Account Created!",
            "username": TEST_USERNAME_1,
            "email": TEST_USER_1_EMAIL,
        }, response.json())

    def test_invalid_signup_POST(self):
        # passwords don't match
        response = self.client.post(self.signup, {
            "username": TEST_USERNAME_2,
            "email": TEST_USER_2_EMAIL,
            "password": TEST_USER_2_PASSWORD,
            "password2": TEST_USER_1_PASSWORD
        })

        self.assertEquals(response.status_code, 400)

        # email already exists
        response = self.client.post(self.signup, {
            "username": TEST_USERNAME_2,
            "email": TEST_USER_0_EMAIL,
            "password": TEST_USER_2_PASSWORD,
            "password2": TEST_USER_2_PASSWORD
        })

        self.assertEquals(response.status_code, 400)

        # username already exists
        response = self.client.post(self.signup, {
            "username": TEST_USERNAME_0,
            "email": TEST_USER_2_EMAIL,
            "password": TEST_USER_2_PASSWORD,
            "password2": TEST_USER_2_PASSWORD
        })

        self.assertEquals(response.status_code, 400)

class TestNotesViews(TestCase):

    def setUp(self):

        self.client = Client()
        self.create_notes = reverse('create-notes')
        self.get_update_notes_by_id = reverse("get-update-notes-by-id", args=[TEST_NOTEID])
        self.share_notes = reverse("share-notes", args=[TEST_NOTEID])
        self.get_version_history = reverse("get-version-history", args=[TEST_NOTEID])

        user = User.objects.create(username=TEST_USERNAME_0, email = TEST_USER_0_EMAIL, password = TEST_USER_0_PASSWORD)
        self.user_0_token = Token.objects.get(user = user)

    def test_create_notes_POST(self):

        response = self.client.post(self.create_notes, json.dumps({"title": "First note for unit test", "content": "This is the first note"}), content_type="application/json", HTTP_AUTHORIZATION = f"Token {self.user_0_token}")

        self.assertEquals(response.status_code, 201)

    def test_get_notes_by_id_GET(self):
        Notes.objects.create(notesId = TEST_NOTEID, title = TEST_NOTE_TITLE, content = TEST_NOTE_CONTENT, isPrivate = True, createdBy = TEST_USERNAME_0, updatedAt = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))

        response = self.client.get(self.get_update_notes_by_id, HTTP_AUTHORIZATION = f"Token {self.user_0_token}")

        self.assertEquals(response.status_code, 200)
        self.assertDictContainsSubset({
            "title": TEST_NOTE_TITLE,
            "content": TEST_NOTE_CONTENT
        }, response.json())

    def test_get_version_GET(self):
        Notes.objects.create(notesId = TEST_NOTEID, title = TEST_NOTE_TITLE, content = TEST_NOTE_CONTENT, isPrivate = True, createdBy = TEST_USERNAME_0, updatedAt = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        NotesVersion.objects.create(versionId = TEST_VERSIONID, notesId = TEST_NOTEID, createdBy = TEST_USERNAME_0, title = TEST_NOTE_TITLE, content = TEST_NOTE_CONTENT, versionNumber = 1, isPrivate = True)
        Notes.objects.filter(notesId = TEST_NOTEID).update(content = TEST_NOTE_CONTENT+" Now I have added updated content.")
        NotesVersion.objects.create(versionId = uuid4(), notesId = TEST_NOTEID, createdBy = TEST_USERNAME_0, title = TEST_NOTE_TITLE, content = TEST_NOTE_CONTENT+" Now I have added updated content.", versionNumber = 2, isPrivate = True)
        
        response = self.client.get(self.get_version_history, HTTP_AUTHORIZATION = f"Token {self.user_0_token}")

        self.assertEquals(response.status_code, 200)
        
        changesMap = response.json()[0]
        
        self.assertDictContainsSubset({
            'linesChanges': [{'diff': ' Now I have added updated content.', 'startIndex': 31, 'endIndex': 64}]
        }, changesMap)

    def test_update_notes_PUT(self):
        Notes.objects.create(notesId = TEST_NOTEID, title = TEST_NOTE_TITLE, content = TEST_NOTE_CONTENT, isPrivate = True, createdBy = TEST_USERNAME_0, updatedAt = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        
        response = self.client.put(self.get_update_notes_by_id, json.dumps({
            "title": "New Title",
            "content": f"{TEST_NOTE_CONTENT}. I want to update the content."
        }), content_type="application/json", HTTP_AUTHORIZATION = f"Token {self.user_0_token}")

        self.assertEquals(response.status_code, 202)

    def test_share_notes_POST(self):
        Notes.objects.create(notesId = TEST_NOTEID, title = TEST_NOTE_TITLE, content = TEST_NOTE_CONTENT, isPrivate = True, createdBy = TEST_USERNAME_0, updatedAt = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
        
        User.objects.create(username=TEST_USERNAME_1, email = TEST_USER_1_EMAIL, password = TEST_USER_1_PASSWORD)
        User.objects.create(username=TEST_USERNAME_2, email = TEST_USER_2_EMAIL, password = TEST_USER_2_PASSWORD)
        
        response = self.client.post(self.share_notes, json.dumps({
            "users": [TEST_USERNAME_1, TEST_USERNAME_2]
        }), content_type="application/json", HTTP_AUTHORIZATION = f"Token {self.user_0_token}")

        self.assertEquals(response.status_code, 200)
        self.assertContains(response, f"Notes shared with username = {TEST_USERNAME_1}")
        self.assertContains(response, f"Notes shared with username = {TEST_USERNAME_2}")
