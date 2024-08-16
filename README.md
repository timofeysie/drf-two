![CI logo](https://codeinstitute.s3.amazonaws.com/fullstack/ci_logo_small.png)

# DRF Two

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

Add the apps to the drf_two\settings.py file.  The app names need to be in this particular order

with django.contrib.staticfiles between  cloudinary_storage and Cloudinary.

drf_two\settings.py

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

```py title="drf_two\settings.py"
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

The Profile model is created with a one-to-one field pointing to a User instance and stores the images in the database.

A Meta class is created that will return a Profile instances where the most recently created is first.  

In the dunder string method returns information about who the profile owner is.

To ensure that a profile is created every time a user is created signal notifications that get triggered when a  
user is created are used.

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

What does the "f" in ```return f"{self.owner}'s profile"``` mean?  I have no idea.  Need to find out.  I didn't take the whole Python/DRF course, just the backend course so I probably missed that.

A quick search shows that:

*It's a type hint. Function f takes argument s of expected type string.*

Open the [docs](https://docs.python.org/3/library/typing.html) linked to that message and search for "f" and it doesn't help.  I would have to read the whole thing which is not a bad idea, but not possible at the moment.

That kind of answer is a kind of RTFM (Read the f***ing Manual) response which made StackOverflow such a game changer where instead of a link to docs, people competed for the best answer in a positive way.

On another reddit thread, someone answered the questions: *Before f-strings we used the format function.* as well as providing a link with an anchor relating to the exact part of the long document where the detail is discussed: https://docs.python.org/3/library/stdtypes.html#str.format*

```py
str.format(*args, **kwargs)
```

Note the original file is [located in the moments repo](https://github.com/Code-Institute-Solutions/drf-api/blob/master/profiles/models.py).

Register the Profile model in admin.py

```py
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)
```

Then run make migrations which you have to do after updating a model:

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

drf_two\urls.py

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

To make this clear overwrite the default behavior to return username instead using ```owner.username```

To access the profile name field a Post serializer like this:

```py
profile_name = serializers.ReadOnlyField(source='owner.profile.name')
```

To add the profile image field to each post, access a sub-attribute, so it would look like this:

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

Here is [the repo for this part](https://github.com/Code-Institute-Solutions/drf-api/tree/025406b0a0fb365a1931747b596c33fd3ba2a6dc).

Just adding this to: drf_two\urls.py automagically adds a login button in the framework webpage view.

```py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    ...
```

The rest framework comes with a set of commonly used permissions such as:

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
from drf_two.permissions import IsOwnerOrReadOnly # <-- note this has to be the name of the app, which is not drf_api

class ProfileDetail(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly] # <--

    def get_object(self, pk):
        try:
            profile = Profile.objects.get(pk=pk)
            self.check_object_permissions(self.request, profile) # <--
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

## The Post module

### Post Serializer Challenge & Adding the Image_Filters & PostList

The Post-Serializer Challenge to create a serializer for a new model.

- python manage.py startapp posts
- create the serializers.py file in the posts folder.
- update the posts\models.py file

Then migrate the new model:

```sh
python manage.py makemigrations
python manage.py migrate
```

Then add an image filter to users uploaded images and validation in the posts/serializers.py.

The [code for this step is here](https://github.com/Code-Institute-Solutions/drf-api).

PostList view get function [code](https://github.com/Code-Institute-Solutions/drf-api/tree/02800dbad36d6f5976853975fd4aa3a302e23a0a) is very similar to the ProfileList view.

The API for listing, retrieving and updating posts will is similar to the profile views but also includes post creation and deletion.

Include scaffolding like this: ```python manage.py startapp posts``` then adding urls.py.

User story: A user who is not logged in should not be able to create a post.

### Post images validation

- Image size larger than 2MB
- Image height larger than 4096px
- Image width larger than 4096px

## The PostDetail view

User story: Anyone should be able to get an individual post.
User story: A user who is the owner of a post should not be able to edit and delete it.

Here are the functions in the posts/view.py:

```py

class PostDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    serializer_class = PostSerializer

    def get_object(self, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(self.request, post)
            return post
        except Post.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(
            post, context={'request': request}
        )
        return Response(serializer.data)

    def put(self, request, pk):
        post = self.get_object(pk)
        serializer = PostSerializer(
            post, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        post = self.get_object(pk)
        post.delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
```

And also add the url to the posts/urls.py file:

```py
urlpatterns = [
    path('posts/', views.PostList.as_view()),
    path('posts/<int:pk>/', views.PostDetail.as_view())
]
```

## Comments & CommentDetail Serializer Challenge

Create a serializer for a new Comments model.

1. create the comments app: ```python manage.py startapp comments```
2. create the comments/serializers.py file with two serializers
3. create the comments model
4. migrate it into the Db
5. add 'comments', to the installed apps

Step 3 again to migrate the new model:

```sh
python manage.py makemigrations
python manage.py migrate
```

Here is the [code](https://github.com/Code-Institute-Solutions/drf-api/tree/3748ed4d93b45dcabdbf0b29b95be27ad644fe2d) for this step.

### CommentList and CommentDetail generic views

User story: Users will be able to retrieve, update and delete a comment by id.

Since this is the same functionality as the posts it would be a lot of repetition in the code.

We only have to swap the Post model and serializer for its Comment counterparts.

comments\views.py

```py
class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

Compare that to posts\views.py:

```py
class PostList(APIView):
    serializer_class = PostSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(
            posts, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(
            data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
```

As you can see, it's a lot leaner. [Django generic views](https://www.django-rest-framework.org/api-guide/generic-views/#attributes/) are a shortcut for common usage patterns.

Instead of specifying the model set the queryset attribute.

The request is a part of the context object by default and doesn't have to be passed manually as in the regular class based views.

Create comments/urls.py with similar functionality as the other endpoints:

```py
urlpatterns = [
    path('comments/', views.CommentList.as_view()),
    path('comments/<int:pk>/', views.CommentDetail.as_view())
]
```

## The likes app, serializer & generic views

- create the likes app: ```python manage.py startapp likes```
- add the model for likes
- migrate the model
- register the app as an INSTALLED APP in settings.py
- create the create the serializers.py
- add path('', include('likes.urls')), to the drf_two/urls.py file

The [solution code](https://github.com/Code-Institute-Solutions/drf-api/tree/d5b167df08db8ef479633393334783af2821f364).

If you like the same post twice you will get an IntegrityError.  

To catch this we do the following:

```py
    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                'detail': 'possible duplicate'
            })
```

The [code for this step](https://github.com/Code-Institute-Solutions/drf-api/blob/c3ba26abf5038edc1c26197775d1c09bae9f67cc/drf_api/urls.py).

## Followers

Follower Model, serializers and generic views.

- create the followers app: ```python manage.py startapp followers```
- register the app in INSTALLED APP in settings.py
- make and run your migrations
- create the serializers.py file in the followers folder
- add the model code
- create a new followers/urls.py file
- In urls/urls.py add the url patterns path('', include('followers.urls')),

The [solution Code](https://github.com/Code-Institute-Solutions/drf-api/blob/a52eb3634a052033c8bf575a48b3d588c28da8a6/drf_api/urls.py).

https://github.com/Code-Institute-Solutions/drf-api/blob/23b93337ab45903140ea01232474e9fbcad4f015/profiles/views.py

## Refactoring Post and Profile Views

Refactor the Profiles views to use Generic Views.

We can refactor the Post views to use Generic Views later:
the [Post Views Refactor Source Code](https://github.com/Code-Institute-Solutions/drf-api/blob/23b93337ab45903140ea01232474e9fbcad4f015/posts/views.py).

## Adding extra fields to Posts and Profiles

### Following and liking

Here we create two  extra SerializerMethodFields for the Profile and PostSerializer.

User story:  If the logged in user is not following a profile, the following_id says null.

User story: If a user is logged in and follows a profile, the following_id field has their id.

So the following_id field in the /profiles list should match the id in the /followers list.

When a user un-follows them, we know which Follower instance to delete and the following_id will go back to null.

User story: A logged out users can't follow a profile.

For this functionality we add following_id to the ProfileSerializer

Similar to this we want to add the like_id to the posts SerializerMethodField

The [source code](https://github.com/Code-Institute-Solutions/drf-api/blob/6095fae29d4a24d87f9a2ff6dfe4a36f122f5d67/posts/serializers.py) for this section.

### Sorting

Next we add sortable fields to Profiles and Posts using the annotate method  
on ProfileList and PostList view querysets.

The finished moments app makes this api/profiles/?ordering=-followers_count GET with result objects like this:

```json
{
    "id": 1,
    "owner": "sean",
    "created_at": "11 Oct 2022",
    "updated_at": "23 Jan 2023",
    "name": "",
    "content": "",
    "image": "https://res.cloudinary.com/nazarja/image/upload/v1/media/images/default_profile_qdjgyp_rzjy8m",
    "is_owner": false,
    "following_id": 1,
    "posts_count": 2,
    "followers_count": 1,
    "following_count": 0
}
```

Here is where we add the last three fields and order profiles by fields in an ascending and descending order.

In profiles/views.py before we just did this:

```py
queryset = Profile.objects.all()
```

Now, it will look like this:

```py
    queryset = Profile.objects.annotate(
        posts_count=Count('owner__post', distinct=True),
        followers_count=Count('owner__followed', distinct=True),
        following_count=Count('owner__following', distinct=True)
    ).order_by('-created_at')
    serializer_class = ProfileSerializer
    filter_backends = [
        filters.OrderingFilter
    ]
    ordering_fields = [
        'posts_count',
        'followers_count',
        'following_count',
        'owner__following__created_at',
        'owner__followed__created_at',
    ]
```

That's a lot of cheddar.

For the posts count, since there is no direct relationship between Profile and Post so go through the User model to connect them.

For the followers/following Within we have two foreign keys that are referencing the User model:

1. the User following another user (owner following)
2. the one being followed (followed)

I understand what "owner__followed" is doing in the followers_count.  I see how it goes from the owner in the Profile table through the User table to the followed field in the Follower table.  It's via the foreign key, so that makes sense.  But the second one ```following_count=Count('owner__following', distinct=True)``` is a bit harder to reason about.

It goes from the User via the owner field and then reference the "following" field which I thought was called "owner" but is referred to as the "related_name",  

It would help to look at these table definitions.

#### profiles

```py
owner = models.OneToOneField(User, on_delete=models.CASCADE)
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
name = models.CharField(max_length=255, blank=True)
content = models.TextField(blank=True)
image = models.ImageField(upload_to='images/', default='...')
```

#### user

```py
from django.contrib.auth.models import User
```

#### follower

```py
owner = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
followed = models.ForeignKey(User, related_name='followed', on_delete=models.CASCADE)
created_at = models.DateTimeField(auto_now_add=True)
```

OK, I see.  It makes it clear with the related_name field.  Now that makes sense.

This is why I take these notes.  It helps to explain it to myself so that I can get clear about it.  Just watching a video or reading it fades away fast.  Notes stay behind and if I forget again, I just read the notes.

These fields are also added as ReadOnly fields to the Profile Serializer:

```py
class ProfileSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    following_id = serializers.SerializerMethodField()
    posts_count = serializers.ReadOnlyField()
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
```

Also the fields array at the bottom of that file as well as be added to the profiles/views.py detail view.  Neat.

### Extra fields for the post

Next add two new fields for a retrieved posts queryset:

- comments_count
- likes_count

Also add these fields to the fields list in posts/serializer.py.

The [code for this step](https://github.com/Code-Institute-Solutions/drf-api/blob/a7033eacc714c79df49679fbebd455e300e09d95/posts/serializers.py).

## Searching & Filtering

### Search

User story: As a user I want to search posts by either the title or the author’s name.

Django makes it easy.  It's as simple as this:

```py
class PostList(generics.ListCreateAPIView):
    ...
    search_fields = [
        'owner__username',
        'title',
    ]
```

There will automatically be a search field in the admin view now.

### Filtering the feed

Adding the filter feature to our API

User story: As a user I want to show posts that are owned by users that a particular user is following, liked by a particular user, and owned by a particular user.

First run this and and add it to INSTALLED_APPS in settings.py.

```sh
pip install django-filter
```

After installing a library and its working, we update dependencies file:

```sh
pip freeze > requirements.txt
```

To get the user post feed by their profile id we follow these steps:

- find out who owns each post in the database
- see if a post owner is being followed by a suer
- point to the users profile to use its id to filter the results

For example, user John.  We get his instance in the User table to find out if anyone is following him.
We refer to the related name "followed" in the followers table.
Ronan is following John, so we return his profile_id by first using the owner field to relate back to User, and then the profile.  

It's similar for the liked posts. When we pass in Ronan's profile id, we should see all the posts that he liked.

The result is an array in the posts/views.py file like this:

```py
filterset_fields = [
    # user feed
    'owner__followed__owner__profile',
    # user liked posts
    'likes__owner__profile',
    # user posts
    'owner__profile',
]
```

And the profile filter for user profiles that follow a user with a given profile_id in profiles/views.py looks like this:

```py
filterset_fields = [
    'owner__following__followed__profile',
    # in order to get all the profiles followed by a users
    'owner__followed__owner__profile',
]
```

In the comments/views.py file, it's a lot easier.

In order to to get all the comments associated with a given post, we only need posts.

## a note on pip vs pip3

It's using pip3.  We have used pip all along so far.  Is this what caused the problem with all auth last time?

Your pip is a soft link to the same executable file path with pip3. you can use the commands below to check where your pip and pip3 real paths are:

```sh
$ ls -l `which pip`
$ ls -l `which pip3`
```

You may also use the commands below to know more details:

```sh
$ pip show pip
$ pip3 show pip
```

## JWTs

I have bunched the changes for installing and configuring JWTs in this section.

Instead of the command pip3 install dj-rest-auth, use dj-rest-auth==2.1.9:

```shell
pip3 install dj-rest-auth==2.1.9
```

```sh
python manage.py migrate
python manage.py makemigrations
```

```sh
pip install 'dj-rest-auth[with-social]'
...
WARNING: dj-rest-auth 2.1.9 does not provide the extra 'with-social'
```

```sh
pip install djangorestframework-simplejwt
```

Much of this section is following [the installation instructions](https://dj-rest-auth.readthedocs.io/en/latest/installation.html) for dj-rest-auth.  JWTs allow the server to be stateless, which is a big part of a REST framework.

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

We will still use session authentication in development and for Production use Tokens.

To make this distinction, set  ```os.environ['DEV'] = '1'``` in the env.py file.

Next, use this value to check whether we’re in Development or Production, and authenticate using sessions or tokens respectively.

To enable token authentication, set REST_USE_JWT to True.

To make sure they’re sent over HTTPS only set JWT_AUTH_SECURE to True.

Declare the cookie names for the access and refresh tokens since we both.

## The problem with allauth again

```sh
$ python manage.py migrate
Traceback (most recent call last):
  File "C:\Users\timof\repos\timo\drf-two\manage.py", line 22, in <module>
    main()
  File "C:\Users\timof\repos\timo\drf-two\manage.py", line 18, in main
    execute_from_command_line(sys.argv)
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\site-packages\django\core\management\__init__.py", line 419, in execute_from_command_line
    utility.execute()
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\site-packages\django\core\management\__init__.py", line 395, in execute
    django.setup()
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\site-packages\django\__init__.py", line 24, in setup
    apps.populate(settings.INSTALLED_APPS)
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\site-packages\django\apps\registry.py", line 122, in populate
    app_config.ready()
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\site-packages\allauth\account\apps.py", line 17, in ready
    raise ImproperlyConfigured(
django.core.exceptions.ImproperlyConfigured: allauth.account.middleware.AccountMiddleware must be added to settings.MIDDLEWARE
```

OK, OK, I will add that.  It's not in the [official source](https://github.com/Code-Institute-Solutions/drf-api/blob/c637122d1a559139cabf1d39b0a3281814091d79/drf_api/settings.py) but have to sort this out.  Its a few years old.

Next issue:

```sh
ModuleNotFoundError: No module named 'drf_two.serializers'
```

Create drf_two/serializers.py

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

### Fixing the allauth errors

Run migrations:

```shell
python manage.py migrate
...
ModuleNotFoundError: No module named 'allauth'
```

Trying to install that and I get this on migrate:

```sh
ImportError: allauth needs to be added to INSTALLED_APPS.
```

A [StackOverflow answer](https://stackoverflow.com/questions/76969410/importerror-allauth-needs-to-be-added-to-installed-apps) says to use this version:

```sh
pip install django-allauth==0.54.0
```

Then I see this error when running the server:

```sh
PS C:\Users\timof\repos\timo\drf-two> python manage.py runserver             
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
February 03, 2024 - 15:45:08
Django version 3.2, using settings 'drf_two.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
Exception in thread django-main-thread:
Traceback (most recent call last):
...
  File "<frozen importlib._bootstrap>", line 1004, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'allauth.account.middleware'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\threading.py", line 1016, in _bootstrap_inner
    self.run()
  ...
  File "C:\Users\timof\AppData\Local\Programs\Python\Python310\lib\site-packages\django\core\servers\basehttp.py", line 47, in get_internal_wsgi_application
    raise ImproperlyConfigured(
django.core.exceptions.ImproperlyConfigured: WSGI application 'drf_two.wsgi.application' could not be loaded; Error importing module.
```

I panicked for a second and thought my name was the issue: 'drf_two' and not 'drf_api', but I searched for the first error *No module named 'allauth.account.middleware'* and found this [StackOverlow](https://stackoverflow.com/questions/77012106/django-allauth-modulenotfounderror-no-module-named-allauth-account-middlewar) which solved the action and we are back in business.

*The middleware is only present in the unreleased 0.56.0-dev, likely you are using 0.55.2 and following 0.56 documentation.
*The culprit is the Middleware entry.*

```py
"allauth.account.middleware.AccountMiddleware", # remove this
```

Lastly, update the deps:

```sh
pip freeze > requirements.txt
```

## Preparing the API for deployment

In order to prepare our API for deployment here are some extra tasks.

- add the root route to our API
- add pagination to all ListViews
- add a default JSON renderer for production
- add [date time formatting](https://www.django-rest-framework.org/api-guide/settings/#date-and-time-formatting) for all the  created_at and updated_at fields
- create a Db to be used when the app is deployed

### Create a database

Instructions to [set up an account with ElephantSQL.com.](https://code-institute-students.github.io/deployment-docs/02-elephantsql/elephantsql-01-sign-up)

[ElephantSQL.com](https://www.elephantsql.com/)

```txt
Instance name: DRF Two Team
Account type: Tiny Turtle
Total: Free
Name: drf-two
Provider: Amazon Web Services
Region: AP-NorthEast-1 (Tokyo)
```

### Create a Heroku app

The process to create a new app on Heroku is documented on their site.

- log into the Heroku Dashboard
- click "New" and "Create new app"
- name the app and select the region
- in Settings tab add a Config Var DATABASE_URL with the database URL from ElephantSQL value

When trying to add a Config Var DATABASE_URL in Heroku with the value of my database URL from ElephantSQL, I got this error: *item could not be updated: Unknown error*

In the console I saw this:

```txt
state-machine.js:24 
       GET https://kolkrabbi.heroku.com/apps/bc714071-7dd3-45de-bc6d-a43b63fe0000/github 404 
Access to XMLHttpRequest at 'https://api.heroku.com/apps/bc714071-7dd3-45de-bc6d-a43b63fe0000/config-vars' from origin 'https://dashboard.heroku.com' has been blocked by CORS policy: Method PATCH is not allowed by Access-Control-Allow-Methods in preflight response.
state-machine.js:24             
   PATCH https://api.heroku.com/apps/bc714071-7dd3-45de-bc6d-a43b63fe0000/config-vars net::ERR_FAILED
(anonymous) @ state-machine.js:24
g @ chunk.5.9f71834c517a7a7113bd.js:96
scheduleTask @ chunk.5.9f71834c517a7a7113bd.js:13
…
```

Searching in the Heroku docs for that error, I saw a recommendation to clear the browser cache, use incognito mode or use a different browser.  So I fired up Edge and that worked to set the config variable.

### Project preparation for your IDE

In the terminal, install dj_database_url and psycopg2, both of these are needed to connect to your external database

```sh
pip3 install dj_database_url==0.5.0 psycopg2
```

In your settings.py file, import dj_database_url underneath the import for os

```py
import os
import dj_database_url
```

Currently, in the settings.py file we have this:

```py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Step 3: The instructions say to update the "database section" to this:

```py
 if 'DEV' in os.environ:
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.sqlite3',
             'NAME': BASE_DIR / 'db.sqlite3',
         }
     }
 else:
     DATABASES = {
         'default': dj_database_url.parse(os.environ.get("DATABASE_URL"))
     }
```

To confirm this location I looked at [the complete moments source code](https://github.com/Code-Institute-Solutions/drf-api/blob/master/drf_api/settings.py) and saw this:

```py
DATABASES = {
    'default': ({
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    } if 'DEV' in os.environ else dj_database_url.parse(
        os.environ.get('DATABASE_URL')
    ))
}
```

So I'm not sure why those are different.

Moving on, add the Db url to the env.py file:

```py
os.environ['DATABASE_URL'] = "<your PostgreSQL URL here>"
```

Step 5: *Temporarily comment out the DEV environment variable so that your IDE can connect to your external database*

That's also in the env.py file, although this detail is left out.

Step 7: In the terminal, -–dry-run your makemigrations to confirm you are connected to the external database

```sh
python3 manage.py makemigrations --dry-run
Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Manage App Execution Aliases.
```

So I assume that should just be 'python'.  But I see the comment added to the if 'DEV' block, so that's good.  Remove that and move on.

Migrate your database models to your new database

```py
python3 manage.py migrate
```

Create a superuser for your new database

```py
python3 manage.py createsuperuser
```

Again, I will use 'python' and not 'python3' here.

```sh
$ python manage.py migrate
Operations to perform:
  Apply all migrations: account, admin, auth, authtoken, comments, contenttypes, followers, likes, posts, profiles, sessions, sites, socialaccount
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying account.0001_initial... OK
  Applying account.0002_email_max_length... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying authtoken.0001_initial... OK
  Applying authtoken.0002_auto_20160226_1747... OK
  Applying authtoken.0003_tokenproxy... OK
  Applying posts.0001_initial... OK
  Applying posts.0002_post_image_filter... OK
  Applying comments.0001_initial... OK
  Applying followers.0001_initial... OK
  Applying likes.0001_initial... OK
  Applying profiles.0001_initial... OK
  Applying sessions.0001_initial... OK
  Applying sites.0001_initial... OK
  Applying sites.0002_alter_domain_unique... OK
  Applying socialaccount.0001_initial... OK
  Applying socialaccount.0002_token_max_lengths... OK
  Applying socialaccount.0003_extra_data_default_dict... OK
  ```

### confirm that the data in your database on ElephantSQL has been created

1. On the ElephantSQL page for your database, in the left side navigation, select “BROWSER”
2. Click the Table queries button, select auth_user

This worked for me the second time.

### prepare the project for deployment to Heroku

This includes

- installing a package needed to run the project on Heroku
- fixing a few environment variables
- creating a Procfile file that will provide the commands to Heroku to build and run the project

In the terminal install gunicorn

```sh
pip3 install gunicorn django-cors-headers
```

Update your requirements.txt

```sh
pip freeze --local > requirements.txt
```

Create a Procfile file required by Heroku.

Remember, it must be named correctly and not have any file extension, otherwise Heroku won’t recognise it

Inside the Procfile, add these two commands

```sh
release: python manage.py makemigrations && python manage.py migrate
web: gunicorn drf_two.wsgi
```

In settings.py file, update the value of the ALLOWED_HOSTS variable to include your Heroku app’s URL

```py
ALLOWED_HOSTS = ['localhost', '<your_app_name>.herokuapp.com']
```

Add corsheaders to INSTALLED_APPS

```py
INSTALLED_APPS = [
    ...
    'dj_rest_auth.registration',
    'corsheaders',
    ...
 ]
```

Add corsheaders middleware to the TOP of the MIDDLEWARE

```py
 SITE_ID = 1
 MIDDLEWARE = [
     'corsheaders.middleware.CorsMiddleware',
     ...
 ]
```

Under the MIDDLEWARE list, set the ALLOWED_ORIGINS for the network requests made to the server with the following code:

```py
if 'CLIENT_ORIGIN' in os.environ:
     CORS_ALLOWED_ORIGINS = [
         os.environ.get('CLIENT_ORIGIN')
     ]
else:
     CORS_ALLOWED_ORIGIN_REGEXES = [
         r"^https://.*\.gitpod\.io$",
     ]
```

Here the allowed origins are set for the network requests made to the server. The API will use the CLIENT_ORIGIN variable, which is the front end app's url. We haven't deployed that project yet, but that's ok. If the variable is not present, that means the project is still in development, so then the regular expression in the else statement will allow requests that are coming from your IDE.

Enable sending cookies in cross-origin requests so that users can get authentication functionality

```py
else:
     CORS_ALLOWED_ORIGIN_REGEXES = [
         r"^https://.*\.gitpod\.io$",
     ]

CORS_ALLOW_CREDENTIALS = True
```

To be able to have the front end app and the API deployed to different platforms, set the JWT_AUTH_SAMESITE attribute to 'None'. Without this the cookies would be blocked

```py
JWT_AUTH_COOKIE = 'my-app-auth'
JWT_AUTH_REFRESH_COOKE = 'my-refresh-token'
JWT_AUTH_SAMESITE = 'None'
```

Remove the value for SECRET_KEY and replace with the following code to use an environment variable instead

```py
# SECURITY WARNING: keep the secret key used in production secret
SECRET_KEY = os.getenv('SECRET_KEY')
```

Set a NEW value for your SECRET_KEY environment variable in env.py, do NOT use the same one that has been published to GitHub in your commits

```py
os.environ.setdefault("SECRET_KEY", "RandomValueHere")
```

Set the DEBUG value to be True only if the DEV environment variable exists. This will mean it is True in development, and False in production

```py
DEBUG = 'DEV' in os.environ
```

Comment DEV back in env.py

```py
import os

os.environ['CLOUDINARY_URL'] = "cloudinary://..."
os.environ['SECRET_KEY'] = "Z7o..."
os.environ['DEV'] = '1'
os.environ['DATABASE_URL'] = "postgres://..."
```

Ensure the project requirements.txt file is up to date. In the IDE terminal of your DRF API project enter the following

```sh
pip freeze --local > requirements.txt
```

Add, commit and push to GitHub.

I had some issues here as I was on the develop branch, and I then needed to merge with main, which caused this crisis:

```sh
$ git pull
remote: Enumerating objects: 1, done.
remote: Counting objects: 100% (1/1), done.
remote: Total 1 (delta 0), reused 0 (delta 0), pack-reused 0
Unpacking objects: 100% (1/1), 898 bytes | 299.00 KiB/s, done.
From https://github.com/timofeysie/drf-two
   a415495..82ab13e  main       -> origin/main
Unlink of file 'db.sqlite3' failed. Should I try again? (y/n) n
error: unable to unlink old 'db.sqlite3': Invalid argument
Updating files: 100% (9/9), done.
Updating a415495..82ab13e


$ git status
On branch main
Your branch is behind 'origin/main' by 5 commits, and can be fast-forwarded.
  (use "git pull" to update your local branch)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
        modified:   README.md
        modified:   comments/serializers.py
        modified:   drf_two/settings.py
        modified:   drf_two/urls.py
        modified:   requirements.txt

Untracked files:
  (use "git add <file>..." to include in what will be committed)
        Procfile
        drf_two/serializers.py
        drf_two/views.py

$ git push
To https://github.com/timofeysie/drf-two.git
 ! [rejected]        main -> main (non-fast-forward)
error: failed to push some refs to 'https://github.com/timofeysie/drf-two.git'
hint: Updates were rejected because the tip of your current branch is behind
hint: its remote counterpart. Integrate the remote changes (e.g.
hint: 'git pull ...') before pushing again.
hint: See the 'Note about fast-forwards' in 'git push --help' for details.

timof@BOOK-ANH52UMLGO MINGW64 ~/repos/timo/drf-two (main)
$ git pull
Merge made by the 'ort' strategy.
 db.sqlite3 | Bin 196608 -> 299008 bytes
 1 file changed, 0 insertions(+), 0 deletions(-)
 ```

## Heroku deployment

On the Heroku dashboard for your new app, open the Settings tab and add two more Config Vars:

SECRET_KEY (you can make one up, but don’t use the one that was originally in the settings.py file!)

CLOUDINARY_URL, and for the value, copy in your Cloudinary URL from your env.py file (do not add quotation marks!)

I also see this one in the screenshot, do I need it?

```py
os.environ['DISABLE_COLLECTSTATIC'] = '1'
```

Open the Deploy tab

the deploy tab selected on a heroku app

In the Deployment method section, select Connect to GitHub

Search for your repo and click Connect

Optional: You can click Enable Automatic Deploys in case you make any further changes to the project. This will trigger any time code is pushed to your GitHub repository

As we already have all our changes pushed to GitHub, we will use the Manual deploy section and click Deploy Branch. This will start the build process. When finished, it should look something like this

a log showing a successful build with a button to view the app below

Not so fast.  This is what I saw in the log:

```sh
           raise ImproperlyConfigured("The SECRET_KEY setting must not be empty.")
       django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty.
 !     Error while running '$ python manage.py collectstatic --noinput'.
       See traceback above for details.
       You may need to update application code to resolve this error.
       Or, you can disable collectstatic for this application:
          $ heroku config:set DISABLE_COLLECTSTATIC=1
       https://devcenter.heroku.com/articles/django-assets
 !     Push rejected, failed to compile Python app.
 !     Push failed
```

OK, so set default secret key was the issue.  Revert this change:

```py
SECRET_KEY = os.getenv('SECRET_KEY')
```

to this:

```py
os.environ.setdefault("SECRET_KEY", "RandomValueHere")
```

The the build works and completes.  The app should be deployed, but when opening it, I see this:

```txt
Application error
An error occurred in the application and your page could not be served. If you are the application owner, check your logs for details. You can do this from the Heroku CLI with the command
heroku logs --tail
```

The logs on the side say:

```txt
2024-02-06T03:10:31.220450+00:00 app[web.1]: [2024-02-06 03:10:31 +0000] [7] [INFO] Worker exiting (pid: 7)
2024-02-06T03:10:31.239434+00:00 app[web.1]: [2024-02-06 03:10:31 +0000] [2] [ERROR] Worker (pid:7) exited with code 3
2024-02-06T03:10:31.239787+00:00 app[web.1]: [2024-02-06 03:10:31 +0000] [2] [ERROR] Shutting down: Master
2024-02-06T03:10:31.239823+00:00 app[web.1]: [2024-02-06 03:10:31 +0000] [2] [ERROR] Reason: Worker failed to boot.
2024-02-06T03:10:31.321951+00:00 heroku[web.1]: Process exited with status 3
2024-02-06T03:10:31.349590+00:00 heroku[web.1]: State changed from starting to crashed
2024-02-06T03:10:33.487389+00:00 heroku[router]: at=error code=H10 desc="App crashed" method=GET path="/" host=drf-two-eb17ecbff99f.herokuapp.com request_id=b736c7b1-7df4-413e-9486-f301e8bce1ec fwd="175.124.241.131" dyno= connect= service= status=503 bytes= protocol=https
2024-02-06T03:10:34.275102+00:00 heroku[router]: at=error code=H10 desc="App crashed" method=GET path="/favicon.ico" host=drf-two-eb17ecbff99f.herokuapp.com request_id=570d6d21-ec92-4dd5-90ac-0929aa5a61c4 fwd="175.124.241.131" dyno= connect= service= status=503 bytes= protocol=https
2024-02-06T03:10:43.212347+00:00 heroku[router]: at=error code=H10 desc="App crashed" method=GET path="/" host=drf-two-eb17ecbff99f.herokuapp.com request_id=fea40e0b-b52e-4097-892d-4d3242fd6bf5 fwd="175.124.241.131" dyno= connect= service= status=503 bytes= protocol=https
2024-02-06T03:10:43.709349+00:00 heroku[router]: at=error code=H10 desc="App crashed" method=GET path="/favicon.ico" host=drf-two-eb17ecbff99f.herokuapp.com request_id=8b43f7ba-5bb1-4d72-899d-5b822f2bf692 fwd="175.124.241.131" dyno= connect= service= status=503 bytes= protocol=https
```

According to StackOverflow it's the procfile.  Form experience with Heroku, I also have seen that exited with code 3 before when deploying node apps.

Our procfile:

```py
release: python manage.py makemigrations && python manage.py migrate
web: gunicorn drf_two.wsgiaq
```

I notice that the procfile of another project has this:

```py
web: gunicorn lesson_plan_backend.wsgi
```

That must have been a type error on my part, as the instructions above show wsgi, not wsgiaq.

Making this change, I see this:

```txt
https://drf-two-eb17ecbff99f.herokuapp.com/
Request Method: GET
Status Code: 400 Bad Request (from disk cache)
Remote Address:
```

Again, according to StackOverflow, this is an allowed hosts issue:

We currently have this:

```py
ALLOWED_HOSTS = ['localhost', 'drf-two.herokuapp.com']
```

But our url is: drf-two-eb17ecbff99f.herokuapp.com

So add that and try again.  Adding that to the array actually works!

Go to: https://drf-two-eb17ecbff99f.herokuapp.com/

We see the JSON welcome message from the home screen.

The profiles link also shows a JSON object containing a profile.

### dj-rest-auth Bug Fix

Apparently dj-rest-auth has a bug that doesn’t allow users to log out (ref: DRF Rest Auth Issues).

The issue is that the samesite attribute we set to ‘None’ in settings.py (JWT_AUTH_SAMESITE = 'None') is not passed to the logout view. This means that we can’t log out, but must wait for the refresh token to expire instead.

Proposed Solution
One way to fix this issue is to have our own logout view, where we set both cookies to an empty string and pass additional attributes like secure, httponly and samesite, which was left out by mistake by the library.

Follow the steps below to fix this bug

Step 1: (views.py Repo Link)

1. In drf_two/views.py, import JWT_AUTH settings from settings.py.

2. Write a logout view. Looks like quite a bit, but all that’s happening here is that we’re setting the value of both the access token (JWT_AUTH_COOKIE) and refresh token (JWT_AUTH_REFRESH_COOKIE) to empty strings. We also pass samesite=JWT_AUTH_SAMESITE, which we set to ’None’ in settings.py and make sure the cookies are httponly and sent over HTTPS,

Step 2: (urls.py Repo Link)
3. Now that the logout view is there, it has to be included in drf_two/urls.py . The logout_route also needs to be imported,

4. ... and then included in the urlpatterns list. The important thing to note here is that our logout_route has to be placed above the default dj-rest-auth urls, so that it is matched first.

5. Push your code to GitHub.

6. Return to Heroku, in the Deploy tab, Manually Deploy your code again.dj-rest-auth Bug Fix
 Bookmark this page

### One last thing

In order to use this API with the upcoming Advanced React walkthrough project, we’d like to ask you to add two environment variables in the SETTINGS.py file.

ALLOWED_HOST, so that it’s not hardcoded and you could spin up multiple API instances, as they would all be deployed to different URLs.

In settings.py, in the ALLOWED_HOSTS list, copy your ‘... .herokuapp.com’ string.
ALLOWED_HOSTS = [
    '... .herokuapp.com',
    'localhost',
]
Log in to heroku.com and select your API application.
Click “settings”
Click “Reveal config vars”
Add the new key of ALLOWED_HOST with the value for your deployed Heroku application URL that we copied from settings.py
Back in settings.py, replace your ALLOWED HOSTS list '... .herokuapp.com' string we just copied with the ALLOWED_HOST environment variable.
ALLOWED_HOSTS = [
   os.environ.get('ALLOWED_HOST'),
   'localhost',
]

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
