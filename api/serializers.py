from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notes, NotesVersion, SharedNotes
from uuid import uuid4

class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type": "password"}, write_only = True)
    class Meta:
        model = User
        fields = ["url", "username", "email", "password", "password2"]

        extra_kwargs = {
            "password": {"write_only" : True}
        }

    def save(self):
        password = self.validated_data["password"]
        password2 = self.validated_data["password2"]

        if password != password2:
            raise serializers.ValidationError({"Error": "Password does not match!"})
        
        if User.objects.filter(email = self.validated_data['email']).exists():
            raise serializers.ValidationError({"Error": "Account Already Exists!"})
        
        account = User(email = self.validated_data["email"], username=self.validated_data['username'])
        account.set_password(password)

        account.save()

        return account
    
class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ("__all__")


class NotesVersionSerializers(serializers.ModelSerializer):
    class Meta:
        model = NotesVersion
        fields = ("__all__")

class SharedNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedNotes
        fields = ("__all__")