from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
# Create your models here.

class Notes(models.Model):
    notesId = models.UUIDField(max_length = 100, unique = True)
    createdBy = models.CharField(max_length = 100)
    createdAt = models.DateTimeField(auto_now_add = True)
    updatedAt = models.DateTimeField()
    isPrivate = models.BooleanField(default = True)
    title = models.CharField(max_length = 200)
    content = models.TextField()

    
class NotesVersion(models.Model):
    versionId = models.UUIDField(max_length = 100, unique = True)
    notesId = models.UUIDField(max_length = 100)
    createdBy = models.CharField(max_length = 100)
    createdAt = models.DateTimeField(auto_now_add = True)
    title = models.CharField(max_length = 200)
    content = models.TextField()
    versionNumber = models.IntegerField(default = 1)
    isPrivate = models.BooleanField(default = True)

class SharedNotes(models.Model):
    shareId = models.UUIDField(max_length = 100, unique = True)
    notesId = models.UUIDField(max_length = 100)
    sharedBy = models.CharField(max_length = 100)
    sharedAt = models.DateTimeField(auto_now_add = True)
    sharedWith = models.CharField(max_length = 100)

@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user = instance)
        # print("token created!")
