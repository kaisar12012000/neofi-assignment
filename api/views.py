from django.shortcuts import render
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializers import NotesSerializer, NotesVersionSerializers, SharedNotesSerializer
from .models import Notes, NotesVersion, SharedNotes
from rest_framework import generics
from uuid import uuid4
from datetime import datetime
from django.contrib.auth.models import User
from difflib import SequenceMatcher

def get_line_differences(s1, s2):
    # initialize sequence matcher
    matcher = SequenceMatcher(None, s1, s2)
    # get differences
    differences = matcher.get_opcodes()
    # extract the different substrings and their indices
    different_substrings = []
    for tag, i1, i2, j1, j2 in differences:
        if tag != "equal":
            different_substrings.append({
                "diff": s2[j1:j2],
                "startIndex": j1,
                "endIndex": j2-1,
            })

    for entry in different_substrings:
        if entry['diff'] == "":
            different_substrings.remove(entry)

    return different_substrings

# Create your views here.

@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def registerUser(request):
    if request.method == "POST":
        serialzer = UserSerializer(data = request.data)

        data = {}
        status_code = status.HTTP_200_OK

        if serialzer.is_valid():
            account = serialzer.save()
            data["response"] = "Account Created!"
            data["username"] = account.username
            data["email"] = account.email
            
            token = Token.objects.get(user = account).key

            data["token"] = token

        else:
            data = serialzer.errors
            status_code = status.HTTP_400_BAD_REQUEST

        return Response(data, status=status_code)


@api_view(["GET","POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_notes_view(request):
    if request.method == "GET":
        notes = Notes.objects.all()
        serializer = NotesSerializer(notes, many=True)
        return Response(data = serializer.data, status=status.HTTP_200_OK)
    req_data = request.data
    curr_dt = datetime.utcnow()
    iso_dt = curr_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    req_data["notesId"] = uuid4()
    req_data["updatedAt"] = iso_dt
    req_data["createdBy"] = request.user.username
    req_data["isPrivate"] = True
    # version obj
    versionObj = {}
    versionObj['versionId'] = uuid4()
    versionObj['notesId'] = req_data["notesId"]
    versionObj['createdBy'] = request.user.username
    # versionObj['createdAt'] = iso_dt 
    versionObj['title'] = req_data['title']
    versionObj['content'] = req_data['content']
    versionObj['versionNumber'] = 1
    versionObj['isPrivate'] = True 
    serializer = NotesSerializer(data = req_data)
    versionSerializer = NotesVersionSerializers(data = versionObj)
    if serializer.is_valid() and versionSerializer.is_valid():
        serializer.save()
        versionSerializer.save()
        return Response(status= status.HTTP_201_CREATED)
    else:
        return Response(data = {"notes_save_error": serializer.errors, "version_save_error": versionSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["GET", "PUT"])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_update_notes_by_id_view(request, pk):
    username = request.user.username
    notes = Notes.objects.all()
    notes = notes.filter(notesId = pk)
    oldNotes = notes[0]
    versions = NotesVersion.objects.all().filter(notesId=pk)

    if len(notes) > 0: # if notes exists
        serializer = NotesSerializer(notes[0], many=False)
        if (notes[0].createdBy != username): # check if user does not own
            if notes[0].isPrivate: # check if private
                return Response(data={"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            # if not private
            sharedNotes = SharedNotes.objects.all()
            if len(sharedNotes.filter(notesId = pk, sharedWith = username)) <= 0: # check if not shared with user
                 return Response(data={"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            # if shared with user
            if request.method == "PUT":
                ut = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                Notes.objects.filter(notesId = pk).update(title = request.data['title'], content = request.data['content'],  updatedAt = ut)
                versionObj = {
                    "versionId": uuid4(), "notesId": oldNotes.notesId, "createdBy": username, "title": request.data['title'], "content": request.data['content'], "versionNumber": len(versions) + 1, "isPrivate": oldNotes.isPrivate
                }
                versionSerializer = NotesVersionSerializers(data = versionObj)
                if not versionSerializer.is_valid():
                    return Response(data={"version_save_error": versionSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                versionSerializer.save()
                return Response(status=status.HTTP_202_ACCEPTED)
            return Response(data = serializer.data, status=status.HTTP_200_OK)
        # if user owns
        if request.method == "PUT":
            ut = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
            Notes.objects.filter(notesId = pk).update(title = request.data['title'], content = request.data['content'],  updatedAt = ut)
            versionObj = {
                    "versionId": uuid4(), "notesId": oldNotes.notesId, "createdBy": username, "title": request.data['title'], "content": request.data['content'], "versionNumber": len(versions) + 1, "isPrivate": oldNotes.isPrivate
                }
            versionSerializer = NotesVersionSerializers(data = versionObj)
            if not versionSerializer.is_valid():
                return Response(data={"version_save_error": versionSerializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            versionSerializer.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        return Response(data = serializer.data, status=status.HTTP_200_OK)
    # if no notes exist
    return Response(data={"error": "Invalid NotesId provided"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def share_notes_view(request, pk):
    username = request.user.username
    notes = Notes.objects.all()
    notes = notes.filter(notesId=pk, createdBy = username)
    resData = []
    # check if user owns the notes
    if len(notes) <= 0: # if user does not own notes
        return Response(data = {"Error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    # is owns
    # check if users to be shared with exist
    
    for u_name in request.data["users"]:
        sharedWith = User.objects.all().filter(username = u_name)
        if len(sharedWith) <= 0: # user to be shared with does not exists
            resData.append(f"User with username = {u_name} does not exists.")
        else: # user to be shared with exists
            req_data = {
                "shareId": uuid4(),
                "notesId": pk,
                "sharedBy": username,
                "sharedAt": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                'sharedWith': u_name
            }
            sharedSerializer = SharedNotesSerializer(data=req_data)
            if not sharedSerializer.is_valid(): # if validation issue arises
                resData.append(f"Notes could note be shared with user with username = {u_name}.")
            else:
                Notes.objects.filter(notesId = pk).update(isPrivate = False, updatedAt = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
                sharedSerializer.save()
                resData.append(f"Notes shared with username = {u_name}")
    return Response(data={"data": resData}, status=status.HTTP_200_OK)

@api_view(["GET"])
@authentication_classes([SessionAuthentication, BasicAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_version_history(request, pk):
    username = request.user.username
    notes = Notes.objects.all()
    notes = notes.filter(notesId = pk)

    if len(notes) > 0: # if notes exists
        if (notes[0].createdBy != username): # check if user does not own
            if notes[0].isPrivate: # check if private
                return Response(data={"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            # if not private
            sharedNotes = SharedNotes.objects.all()
            if len(sharedNotes.filter(notesId = pk, sharedWith = username)) <= 0: # check if not shared with user
                 return Response(data={"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        # if user owns or shared with user
        versions = NotesVersion.objects.filter(notesId = pk)
        # versions = NotesVersionSerializers(data=versions, many = True)
        dataMap = []
        # print(versions)
        for version in versions:
            dataMap.append(
                {
                    "createdAt": version.createdAt,
                    "updatedBy": version.createdBy,
                    "latestContent": notes[0].content,
                    "oldContent": version.content,
                    "changedTitle" : version.title,
                    "linesChanges" : get_line_differences(version.content, notes[0].content),
                    "versionNumber": version.versionNumber
                })
        return Response(data = dataMap, status=status.HTTP_200_OK)
    # if no notes exist
    return Response(data={"error": "Invalid NotesId provided"}, status=status.HTTP_400_BAD_REQUEST)