from django.contrib import admin
from .models import Notes, NotesVersion, SharedNotes
# Register your models here.

admin.site.register(Notes)
admin.site.register(NotesVersion)
admin.site.register(SharedNotes)
