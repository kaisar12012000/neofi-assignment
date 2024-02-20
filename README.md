# Notes App Backend (Django)

A backend app built using django.

## Table of contents
#### 1. Requirements
#### 2. Installation
#### 3. API Documentation

## Requirements
- difflib
- uuid
- python

## Installation
The first step is to clone the repository. Run the followinf command to clone the github repository.

```bash
git clone https://github.com/kaisar12012000/neofi-assignment.git
```
Verify that you are on branch `main`
```bash
git branch
```
Once the repository is cloned and we have verified the branch it is time to create our virtual environment where we will install all dependecies and run our code. Run the following command to create a virtual environment.
```bash
cd neofi-assignment
py -m venv env # feel free to change the python keyword based on your system (could be python or python3 instead of py)
```
The command should create a new folder/directory named `env`.

Now we must install all dependencies in our virtual environment after activating it. To activate the virtual environment run the following command.
```bash
./env/Scripts/activate # for windows only. Please alter this command based on your OS

```
Now we intall all dependencies.
Run the following command to install `django` and `djamorestframework`. These are the dependencies we are going to use.
```bash
# You are in virtual environment
pip install django
pip install djangorestframework
```
Once both the dependencies are installed we will migrations to set our database.
Run the following command.
```bash
py manage.py migrate
```
Once the migrations are run it is time to start the server and run the unit test cases to verify that the setup is complete.
Run the following command to start server.
```bash
py manage.py runserver
```
Open a seperate terminal and activate your virtual environment here too. Run the following command to start your virtual environment in the new terminal and run unit tests.
```bash
./env/Scripts/activate
# after activation of virtual environment on new terminal run:
py manage.py test api
```
The unit tests will start to run.
There are total 14 unit test cases and it is important for all pass for the set up to be complete.

Now that all tests have passed the server is ready to be used at http://127.0.0.1:8000/

## API documentation
1. ### Register User (sigup):
   - Endpoint : http://127.0.0.1:8000/api/signup/
   - Method : `POST`
   - Request Body :
     ```json
     {
        "username":"UniqueUserName",
        "email":"UniqueEmailId@gmail.com",
        "password"	: "passwordStr",
        "password2": "passwordStr"
     }
     ```
   - Successful Response: (status code = 200)
     ```json
     {
        "response": "Account Created!",
        "username": "UniqueUserName",
        "email": "UniqueEmailId@gmail.com",
        "token": "65fa6ce386fcbac7a4a17b3e28ad9eba2b94ace1"
     }
     ```
2. ### Login User:
   - Endpoint : http://127.0.0.1:8000/api/login/
   - Method : `POST`
   - Request Body :
     ```json
     {
        "username": "Kamrunnahar",
        "password": "kkkk@78612"
     }
     ```
   - Successful Response: (status code = 200)
     ```json
     {
        "token": "65fa6ce386fcbac7a4a17b3e28ad9eba2b94ace1"
     }
     ```
3. ### Create notes:
   - Endpoint : http://127.0.0.1:8000/api/notes/create/
   - Method : `POST`
   - Request Body :
     ```json
     {
        "title": "First note with version",
        "content": "Frist version should be added"
     }
     ```
   - Request Headers :
     ```json
     {
        "Authorization": "Token <token-value>"
     }
     ```
   - Successful Response: (status code = 201)
4. ### Get Notes By Id:
   - Endpoint : http://127.0.0.1:8000/api/notes/:id
   - Method : `GET`
   - Request Headers :
     ```json
     {
        "Authorization": "Token <token-value>"
     }
     ```
   - Successful Response: (status code = 200)
     ```json
     {
       "id": 1,
       "notesId": "22da3018-56ba-450b-b831-4dff9a83b9db",
       "createdBy": "UniqueUserName",
       "createdAt": "2024-02-20T11:10:55.397717Z",
       "updatedAt": "2024-02-20T11:10:55Z",
       "isPrivate": true,
       "title": "First note with version",
       "content": "Frist version should be added"
     }
     ```
5. ### Update Notes By Id:
   - Endpoint : http://127.0.0.1:8000/api/notes/:id
   - Method : `PUT`
   - Request Body :
     ```json
     {
        "title": "Update note with version",
        "content": "Frist version should be added. New content added after the old content" // always the entire content is passed. Changes and version tracking is done my backend system.
     }
     ```
   - Request Headers :
     ```json
     {
        "Authorization": "Token <token-value>"
     }
     ```
   - Successful Response: (status code = 202)
6. ### Share notes:
   - Endpoint : http://127.0.0.1:8000/api/notes/share/:id
   - Method : `POST`
   - Request Body :
     ```json
     {
        "users": ["UniqueUserName", "NonExistentUser"]
     }
     ```
   - Request Headers :
     ```json
     {
        "Authorization": "Token <token-value>"
     }
     ```
   - Successful Response: (status code = 200)
     ```json
     {
        "data": [
          "Notes shared with username = UniqueUserName", // user exists
          "User with username = NonExistentUser does not exists." // user does not exists
         ]
     }
     ```
7. ### Get Version history:
   - Endpoint : http://127.0.0.1:8000/api/notes/version-history/:id
   - Method : `GET`
   - Request Headers :
     ```json
     {
        "Authorization": "Token <token-value>"
     }
     ```
   - Successful Response: (status code = 200)
     ```json
     [
      { // old version
        "createdAt": "2024-02-20T11:10:55.404469Z",
        "updatedBy": "UniqueUserName",
        "latestContent": "Frist version should be added. New content added after the old content",
        "oldContent": "Frist version should be added",
        "changedTitle": "First note with version",
        "linesChanges": [
          {
            "diff": ". New content added after the old content",
            "startIndex": 29,
            "endIndex": 69
          }
        ],
       "versionNumber": 1
      },
      { // latest version
         "createdAt": "2024-02-20T11:29:52.072634Z",
         "updatedBy": "UniqueUserName",
         "latestContent": "Frist version should be added. New content added after the old content",
         "oldContent": "Frist version should be added. New content added after the old content",
         "changedTitle": "new title",
         "linesChanges": [],
         "versionNumber": 2
      }
     ]
     ```
