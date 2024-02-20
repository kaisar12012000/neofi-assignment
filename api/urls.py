from django.urls import path
from .views import registerUser, create_notes_view, get_update_notes_by_id_view, share_notes_view, get_version_history
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path("signup/", registerUser, name="signup"),
    path("login/", obtain_auth_token, name="login"),
    path("notes/create/", create_notes_view, name="create-notes"),
    path("notes/<str:pk>", get_update_notes_by_id_view, name="get-update-notes-by-id"),
    path("notes/share/<str:pk>", share_notes_view, name="share-notes"),
    path("notes/version-history/<str:pk>", get_version_history, name="get-version-history"),
]