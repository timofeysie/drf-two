![CI logo](https://codeinstitute.s3.amazonaws.com/fullstack/ci_logo_small.png)

# Django Rest Framework API Two

The DRF-API project is based on the [Code Institute Django REST Framework](https://github.com/Code-Institute-Org/ci-full-template) module.

## Workflow

```shell
python manage.py runserver
python manage.py migrate
python manage.py makemigrations xyz
python manage.py shell # Use quit() or Ctrl-Z plus Return to exit
python manage.py createsuperuser
python manage.py test zyx # run the sample test
pip freeze > requirements.txt # update dependencies file
```

## Starting the project

Install the specific version of Django needed for the course.

Start the project and install the dependencies.

```shell
> pip3 install 'django<4'
> django-admin startproject drf_two .
> pip install django-cloudinary-storage
> pip install pillow
Requirement already satisfied: Pillow in c:\users\timof\appdata\local\programs\python\python310\lib\site-packages (10.1.0)
```

The Django Cloudinary storage library connects Django to a service that will host the images for the API.

The Pillow library adds image processing capabilities that needed for working with Cloudinary.

Add the apps to the drf_api\settings.py file.  The app names need to be in this particular order

with django.contrib.staticfiles between  cloudinary_storage and Cloudinary.

drf_api\settings.py

```py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
]
```

Next create the env.py file in the top directory to use the Cloudinary API key:

```py title="env.py"
import os
os.environ['CLOUDINARY_URL'] = 'CLOUDINARY_URL=cloudinary://...'
```

In settings.py again load the environment variable needed to set a variable called CLOUDINARY_STORAGE.
Use the environment variable set in the env.py file to declare that value.
Define a setting called MEDIA_URL, which is the standard Django folder to store media so the settings know where to put image files.
Also set a DEFAULT_FILE_STORAGE variable.

```py title="drf_api\settings.py"
from pathlib import Path
import os

if os.path.exists('env.py'):
    import env

CLOUDINARY_STORAGE = {
    'CLOUDINARY_URL': os.environ.get('CLOUDINARY_URL')
}

MEDIA_URL = '/media/'
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
```

## Create the profile app

```shell
python manage.py startapp profiles
```

Add it to the installed apps array.

```py
INSTALLED_APPS = [
    'django.contrib.admin',
    ...
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'rest_framework',

    'profiles',
]
```

### The Profile Model

Create our Profile model with a one-to-one field pointing to a User instance and store the images in the database.

Create a Meta class that will return a Profile instances with most recently created is first.  

In the dunder string method return  information about who the profile owner is.

To ensure that a  profile is created every time a user is created use signals notifications that get triggered when a  
user is created.

```py title=models.py
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User


class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    # the default image
    image = models.ImageField(
        upload_to='images/', default='../default_profile_qdjgyp'
    )

    # meta class to return results in reverse orders (minus s)
    class Meta:
        ordering = ['-created_at']

    # dunder method to return who the owner is
    def __str__(self):
        return f"{self.owner}'s profile"

def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(owner=instance)
# The Django signals are notifications that get triggered by an event to run a function
# each time that signal is received such as notification when a user is created so that 
# a profile can  automatically be created alongside it. 
# Built-in Model signals include:  pre_save, post_save, pre_delete and post_delete.
post_save.connect(create_profile, sender=User)
```

Note the original file is [located in the moments repo](https://github.com/Code-Institute-Solutions/drf-api/blob/master/profiles/models.py).

Register the Profile model in admin.py:2

```py
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)
```

Then run make migrations whihc you have to do after updating a model:

```shell
python manage.py makemigrations
python manage.py migrate
```

Create a admin user and provide a password:

```shell
python manage.py createsuperuser
```

Run the server:

```shell
python manage.py runserver
```

Goto the admin url: http://127.0.0.1:8000/admin

Create a file with the dependencies:

```shell
pip freeze > requirements.txt
```

## Rest Framework Serializers

### Install the the Django REST Framework

```shell
pip install djangorestframework
```

Add it after cloudinary at the bottom of the installed apps array in settings.py:

```py
INSTALLED_APPS = [
    ...
    'cloudinary',
    'rest_framework',

    'profiles',
]
```

### Import the APIView and Response classes in views.py

Find the code for this step [here](https://github.com/Code-Institute-Solutions/drf-api/tree/e3c785ad9f0dfaae57766e948b722f0db49ef4dd).

ProfileList will extend APIView similar to Django's View class.

It also provides a few bits of extra functionality such as making sure to receive a Request instances in the view, handling parsing errors, and adding context to Response objects.

Create the ProfileList view and define the get method.

profiles\views.py

```py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profile

class ProfileList(APIView):
    def get(self, request):
        profiles = Profile.objects.all()
        return Response(profiles)
```

### Create profile urls

Create a urls.py file with the profiles path.

```py
from django.urls import path
from profiles import views

urlpatterns = [
    path('profiles/', views.ProfileList.as_view()),
]
```

Include profile urls in the main apps urls.py

drf_api\urls.py

```py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('profiles.urls')),
]
```

Currently if you start the server and go to 'http://127.0.0.1:8000/profiles/' there is an error: Object of type Profile is not JSON serializable which is fixed with a serializer.

### Create the serializer

Creating serializers.py, import serializers from  rest framework and our Profile model.

Specify 'owner' as a ReadOnlyField and populate it with the owner's username.

In the Meta class point to the Profile model and specify the fields we want in the response.

profiles\serializers.py

```py
from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Profile
        # to list all fields all in an array or set to '__all__'  
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'name',
            'content', 'image',
        ]
```

When extending Django's model class using models.models, the id field is created automatically

### Add the serializer to our views.py file

Import the ProfileSerializer, create a ProfileSerializer instance and pass in profiles and many equals True to specify serializing multiple Profile instances.
In the Response send data returned from the serializer.

profiles\views.py

```py
...
from .serializers import ProfileSerializer

class ProfileList(APIView):
    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)
```

Now the JSON user list is returned.

Update dependencies, git add, commit and push all the changes to GitHub.

## Populating Serializer ReadOnly Field using dot notation

This section begins with a discussion of the ‘source’ attribute in the serializer.

In the ProfileSerializer, dot notation is used to populate the owner ReadOnlyField:

```py
class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
```

The User and Profile tables are connected through the owner ```OneToOne``` field in the models.py:

```py
class Profile(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
```

By default, the owner field always returns the user’s id value.

To make this clear we can overwrite the default behavior to return username instead using ```owner.username```

How you would access the profile name field if you were working in the Post serializer?

```py
profile_name = serializers.ReadOnlyField(source='owner.profile.name')
```

To add the profile image field to each post, we need to access a sub-attribute, so it would look like this:

```py
profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
```

## Profile Details View CRUD: GET and PUT

The REST endpoints for the profiles API look like this:

### List View

- /profiles GET list profiles
- /profiles POST create profile

### Detail View

- /profiles/:id GET get profile by id
- /profiles/:id PUT update profile by id
- /profiles/:id DELETE profile by id

The delete endpoints will not be covered in this module, so now we will implement the GET & PUT endpoints.

I notice that the ProfileDetail class in [the repo](https://github.com/Code-Institute-Solutions/drf-api/blob/master/profiles/views.py) is a bit different from what is shown in the tutorial.

In this project, we use ```APIView```.  Note pk = Primary Key.

```py
class ProfileDetail(APIView):
    def get_object(self, pk):
        try:
            profile = Profile.objects.get(pk=pk)
            return profile
        except Profile.DoesNotExist:
            raise Http404
```

In the repo, it has ```generics.RetrieveUpdateAPIView```

```py
class ProfileDetail(generics.RetrieveUpdateAPIView):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = Profile.objects.annotate(
        posts_count=Count('owner__post', distinct=True),
        followers_count=Count('owner__followed', distinct=True),
        following_count=Count('owner__following', distinct=True)
    ).order_by('-created_at')
    serializer_class = ProfileSerializer
```

I guess that will come when permissions are introduced later.

Not that it says "raise Http404".  I mistakenly used 'return' at first and it would return a 200 instead of a 404.

The GET looks like this:

```py
    def get(self, request, pk):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
```

I'm not exactly sure why the pk is used differently in both methods:

- profile = Profile.objects.get(pk=pk)
- profile = self.get_object(pk)

Next, add the details url in profiles/urls.py to use the new class:

```py
urlpatterns = [
    path('profiles/', views.ProfileList.as_view()),
    path('profile/<int:pk>/', views.ProfileDetail.as_view()),
]
```

After this, running the server again, the profiles/ returns this:

```json
[
    {
        "id": 1,
        "owner": "timof",
        "created_at": "2023-12-02T01:18:52.483047Z",
        "updated_at": "2023-12-02T01:18:52.483047Z",
        "name": "",
        "content": "",
        "image": "https://res.cloudinary.com/dr3am91m4/image/upload/v1/media/../cld-sample-5"
    }
]
```

The profile/1 returns:

```json
{
    "id": 1,
    "owner": "timof",
    "created_at": "2023-12-02T01:18:52.483047Z",
    "updated_at": "2023-12-02T01:18:52.483047Z",
    "name": "",
    "content": "",
    "image": "https://res.cloudinary.com/dr3am91m4/image/upload/v1/media/../cld-sample-5"
}
```

### Edit a profile

Here is what the PUT looks like:

```py
    def put(self, request, pk):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, statue=status.HTTP_400_BAD_REQUEST)
```

This works, but the rest framework will automatically render a form based on  the fields we defined in our ProfileSerializer if we set the serializer_class attribute on our ProfileDetail view

In the video, it looks like this:

```py
    def put(self, request, pk):
        serializer_class = ProfileSerializer
```

But the serializer_class is never used in the method.  And it doesn't work.

ChatGPT suggests this:

```py
serializer = self.serializer_class(profile, data=request.data)
```

That doesn't work, but asking again, it points out it should be inside the class definition, not the method definition:

```py
class ProfileDetail(APIView):
    serializer_class = ProfileSerializer
```

Now a proper form appears.

## Authentication & permissions

The video for this seciont is [here](https://learn.codeinstitute.net/courses/course-v1:CodeInstitute+DRF+2021_T1/courseware/b50f474f85af4de69944fa15a1342abd/9e0bea8f758944059ede7f1fc5ac694a/?child=last).

Here is [the repo for this part](https://github.com/Code-Institute-Solutions/drf-api/tree/025406b0a0fb365a1931747b596c33fd3ba2a6dc).

Just adding this to: drf_api\urls.py automagically adds a login button in the framework webpage view.

```py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    ...
```

The rest framework  come with a set of commonly used permissions such as:

- AllowAny
- IsAuthenticated
- IsAdminUser
- custom permissions

We use a custom permissions to return True only if the user is requesting their own profile.

```PY
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user
```

Next connect to the ProfileDetail view in profiles\views.py:

```py
class ProfileDetail(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly] <--

    def get_object(self, pk):
        try:
            profile = Profile.objects.get(pk=pk)
            self.check_object_permissions(self.request, profile) <--
            return profile
        except Profile.DoesNotExist:
            raise Http404
```

Now the PUT form is only on the logged in users page.

Next in the profile serializer add a field

To get access to the currently logged in user in the request object in the serializer it has to be have to passed in with the context object in all ProfileSerializer in the view methods:

```py
serializer = ProfileSerializer(profiles, many=True, context={'request': request})
```

Then it is used in the profiles/serializers.py new get_is_owner method as well as add the field in the Meta class fields array:

```py
class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner
    class Meta:
        model = Profile
        fields = [
            'id', 'owner', 'created_at', 'updated_at', 'name',
            'content', 'image', 'is_owner'
        ]
```

Now the profiles API returns the field:

```json
[
    {
        "id": 2,
        "owner": "zimof",
        "created_at": "2023-12-03T05:15:38.942881Z",
        "updated_at": "2023-12-03T05:15:38.942881Z",
        "name": "",
        "content": "",
        "image": "https://res.cloudinary.com/dr3am91m4/image/upload/v1/media/../cld-sample-5",
        "is_owner": false
    },
    {
        "id": 1,
        "owner": "timof",
        "created_at": "2023-12-02T01:18:52.483047Z",
        "updated_at": "2023-12-03T05:25:55.040490Z",
        "name": "timof",
        "content": "What it is",
        "image": "https://res.cloudinary.com/dr3am91m4/image/upload/v1/media/../cld-sample-5",
        "is_owner": true
    }
]
```

## Further work

I wont be doing all the exercises and additional modules at this time.  Here is a review of what happens next without any code being added.

### Post Serializer Challenge & Adding the Image_Filters

The Post-Serializer Challenge to create a serializer for a new model.
Then add an image filter to users uploaded images.

This repo is just to get the basics of the rest framework, not a comprehensive run-though of the whole course.

### Post module

The API for listing, retrieving and updating posts will is similar to the profile views but also includes post creation and deletion.

I guess it would include scaffolding like this: ```python manage.py startapp posts``` then adding urls.py.

## JWT

I have bunched the changes for installing and configuring JWTs in this section.

Instead of the command pip3 install dj-rest-auth, use dj-rest-auth==2.1.9:

```shell
pip3 install dj-rest-auth==2.1.9
pip install 'dj-rest-auth[with-social]'
pip install djangorestframework-simplejwt
```

Much of this section is following [the installation instructions](https://dj-rest-auth.readthedocs.io/en/latest/installation.html) for dj-rest-auth.  JWTs allow the server to be stateless, which is a big part of a rest framework.

```py
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
```

```py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path(
        'dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')
    ),
    path('', include('profiles.urls')),
]
```

Create drf_api/serializers.py

Paste the code from the docs:

```py
from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers

class CurrentUserSerializer(UserDetailsSerializer):
    profile_id = serializers.ReadOnlyField(source='profile.id')
    profile_image = serializers.ReadOnlyField(source='profile.image.url')

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + (
            'profile_id', 'profile_image'
        )
```

Run migrations:

```shell
python manage.py migrate
...
ModuleNotFoundError: No module named 'allauth'
```

For some reason there is no transcript on this video, so I can't search for allauth in that.

The lib is shown in the [GitHub repo linked to](https://github.com/Code-Institute-Solutions/drf-api/tree/c637122d1a559139cabf1d39b0a3281814091d79).

'allauth' is shown in the settings.py after running this command: pip install 'dj-rest-auth[with-social]'

In docs linked to, it says:

### Registration (optional)

1. *If you want to enable standard registration process you will need to install django-allauth by using pip install 'dj-rest-auth[with_social]'.*
2. *Add django.contrib.sites, allauth, allauth.account, allauth.socialaccount and dj_rest_auth.registration apps to INSTALLED_APPS in your django settings.py:*
3. *Add SITE_ID = 1 to your django settings.py*

All of this looks good.  So how to fix that error?

```sh
pip install django-allauth
```

However, I still see this migration error:

```sh
$ python manage.py migrate
...
ImportError: allauth needs to be added to INSTALLED_APPS.
```

But the INSTALLED_APPS looks good to me:

```py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',

    'profiles',
]
```

Running the server, there are a few dependencies that need installing:

```sh
pip install django-filter
pip install django-cors-headers
```

Then this:

```sh
> python manage.py runserver     
Watching for file changes with StatReloader
Exception in thread django-main-thread:
Traceback (most recent call last):
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\threading.py", line 1016, in _bootstrap_inner
    self.run()
  ...
    raise ImproperlyConfigured("The SECRET_KEY setting must not be empty.")
django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.
```

The settings.py file has this:

```py
SECRET_KEY = 'your_secret_key_value'
```

I generated a key like this:

```py
import secrets

SECRET_KEY = secrets.token_hex(50)
```

Then, moved the key into the env.py file.

```sh
> python manage.py runserver     
Watching for file changes with StatReloader
Exception in thread django-main-thread:
Traceback (most recent call last):
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\threading.py", line 1016, in _bootstrap_inner
    self.run()
...
    raise ImproperlyConfigured(
django.core.exceptions.ImproperlyConfigured: allauth.account.middleware.AccountMiddleware must be added to settings.MIDDLEWARE
```

Here are the apps and middleware in settings.py:

```py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',

    'profiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

As you can see, allauth is in both.  I can see from the [completed settings file](https://github.com/Code-Institute-Solutions/drf-api/blob/master/drf_api/settings.py) that my version matches what I have.

I have a [branch](https://github.com/timofeysie/drf-api/commit/cc77b2a2eed50ca5ba2040df742bf9e8150f7112) with the jump ahead code.  There is still the env.py file:

## Back to work

After trying to jump ahead to give an attempt at just running the whole thing, I ran into issues described above with allauth.

However, when going back to where I was in the tutorial before I jumped ahead and stashing the jump ahead work in a different branch, I am still getting allauth errors.

```py
> python manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

Exception in thread django-main-thread:
Traceback (most recent call last):
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\site-packages\dj_rest_auth\registration\serializers.py", line 17, in <module>
    from allauth.utils import email_address_exists, get_username_max_length
ImportError: cannot import name 'email_address_exists' from 'allauth.utils' (C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\site-packages\allauth\utils.py)

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\threading.py", line 1016, in _bootstrap_inner
    self.run()
 ...
ImportError: allauth needs to be added to INSTALLED_APPS.
```

I have tried to roll everything back to the place where I was the complete profiles section before the "Post Serializer Challenge" section.

So I have used only the INSTALLED_APPS and MIDDLEWARE strings from the last profiles step.

I deleted the __pycache__ directory, as that might still have a trace of allauth in it.

However, I still see the error: RuntimeError: Model class allauth.account.models.EmailAddress doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.


## Useful links

- The official docs for [Django REST framework](https://www.django-rest-framework.org/)
- The [quick-start tutorial](https://www.django-rest-framework.org/tutorial/quickstart/): a simple API to allow admin users to view and edit the users and groups
- The [Tutorial 1: Serialization](https://www.django-rest-framework.org/tutorial/1-serialization/):  a simple pastebin code highlighting Web API

## Original Readme

Welcome USER_NAME,

This is the Code Institute student template for Gitpod. We have preinstalled all of the tools you need to get started. It's perfectly ok to use this template as the basis for your project submissions.

You can safely delete this README.md file, or change it for your own project. Please do read it at least once, though! It contains some important information about Gitpod and the extensions we use. Some of this information has been updated since the video content was created. The last update to this file was: **September 1, 2021**

## Gitpod Reminders

To run a frontend (HTML, CSS, Javascript only) application in Gitpod, in the terminal, type:

`python3 -m http.server`

A blue button should appear to click: _Make Public_,

Another blue button should appear to click: _Open Browser_.

To run a backend Python file, type `python3 app.py`, if your Python file is named `app.py` of course.

A blue button should appear to click: _Make Public_,

Another blue button should appear to click: _Open Browser_.

In Gitpod you have superuser security privileges by default. Therefore you do not need to use the `sudo` (superuser do) command in the bash terminal in any of the lessons.

To log into the Heroku toolbelt CLI:

1. Log in to your Heroku account and go to *Account Settings* in the menu under your avatar.
2. Scroll down to the *API Key* and click *Reveal*
3. Copy the key
4. In Gitpod, from the terminal, run `heroku_config`
5. Paste in your API key when asked

You can now use the `heroku` CLI program - try running `heroku apps` to confirm it works. This API key is unique and private to you so do not share it. If you accidentally make it public then you can create a new one with _Regenerate API Key_.

------

## Release History

We continually tweak and adjust this template to help give you the best experience. Here is the version history:

**September 20 2023:** Update Python version to 3.9.17.

**September 1 2021:** Remove `PGHOSTADDR` environment variable.

**July 19 2021:** Remove `font_fix` script now that the terminal font issue is fixed.

**July 2 2021:** Remove extensions that are not available in Open VSX.

**June 30 2021:** Combined the P4 and P5 templates into one file, added the uptime script. See the FAQ at the end of this file.

**June 10 2021:** Added: `font_fix` script and alias to fix the Terminal font issue

**May 10 2021:** Added `heroku_config` script to allow Heroku API key to be stored as an environment variable.

**April 7 2021:** Upgraded the template for VS Code instead of Theia.

**October 21 2020:** Versions of the HTMLHint, Prettier, Bootstrap4 CDN and Auto Close extensions updated. The Python extension needs to stay the same version for now.

**October 08 2020:** Additional large Gitpod files (`core.mongo*` and `core.python*`) are now hidden in the Explorer, and have been added to the `.gitignore` by default.

**September 22 2020:** Gitpod occasionally creates large `core.Microsoft` files. These are now hidden in the Explorer. A `.gitignore` file has been created to make sure these files will not be committed, along with other common files.

**April 16 2020:** The template now automatically installs MySQL instead of relying on the Gitpod MySQL image. The message about a Python linter not being installed has been dealt with, and the set-up files are now hidden in the Gitpod file explorer.

**April 13 2020:** Added the _Prettier_ code beautifier extension instead of the code formatter built-in to Gitpod.

**February 2020:** The initialisation files now _do not_ auto-delete. They will remain in your project. You can safely ignore them. They just make sure that your workspace is configured correctly each time you open it. It will also prevent the Gitpod configuration popup from appearing.

**December 2019:** Added Eventyret's Bootstrap 4 extension. Type `!bscdn` in a HTML file to add the Bootstrap boilerplate. Check out the <a href="https://github.com/Eventyret/vscode-bcdn" target="_blank">README.md file at the official repo</a> for more options.

------

## FAQ about the uptime script

**Why have you added this script?**

It will help us to calculate how many running workspaces there are at any one time, which greatly helps us with cost and capacity planning. It will help us decide on the future direction of our cloud-based IDE strategy.

**How will this affect me?**

For everyday usage of Gitpod, it doesn’t have any effect at all. The script only captures the following data:

- An ID that is randomly generated each time the workspace is started.
- The current date and time
- The workspace status of “started” or “running”, which is sent every 5 minutes.

It is not possible for us or anyone else to trace the random ID back to an individual, and no personal data is being captured. It will not slow down the workspace or affect your work.

**So….?**

We want to tell you this so that we are being completely transparent about the data we collect and what we do with it.

**Can I opt out?**

Yes, you can. Since no personally identifiable information is being captured, we'd appreciate it if you let the script run; however if you are unhappy with the idea, simply run the following commands from the terminal window after creating the workspace, and this will remove the uptime script:

```
pkill uptime.sh
rm .vscode/uptime.sh
```

**Anything more?**

Yes! We'd strongly encourage you to look at the source code of the `uptime.sh` file so that you know what it's doing. As future software developers, it will be great practice to see how these shell scripts work.

---

Happy coding!
