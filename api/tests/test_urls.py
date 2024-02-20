from django.test import SimpleTestCase
from django.urls import reverse, resolve
from rest_framework.authtoken.views  import obtain_auth_token
from api.views import registerUser, create_notes_view, get_update_notes_by_id_view, get_version_history, share_notes_view

class TestUrls (SimpleTestCase):
    def test_signup_url_is_resolved(self):
        url = reverse("signup")
        self.assertEquals(resolve(url).func , registerUser)

    def test_login_url_is_resolved(self):
        url = reverse("login")
        self.assertEquals(resolve(url).func, obtain_auth_token)

    def test_create_notes_url_is_resolved(self):
        url = reverse("create-notes")
        self.assertEquals(resolve(url).func, create_notes_view)

    def test_get_update_notes_by_id_url_is_resolved(self):
        url = reverse("get-update-notes-by-id", args=["some-notes-id"])
        self.assertEquals(resolve(url).func, get_update_notes_by_id_view)

    def test_share_notes_url_is_resolved(self):
        url = reverse("share-notes", args=["some-notes-id"])
        self.assertEquals(resolve(url).func, share_notes_view)

    def test_get_version_history_url_is_resolved(self):
        url = reverse("get-version-history", args=["some-notes-id"])
        self.assertEquals(resolve(url).func, get_version_history)