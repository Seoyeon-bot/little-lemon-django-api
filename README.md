# 🍋 Little Lemon Django REST API Setup Guide
This guide walks you through setting up a Django REST Framework project for Little Lemon, including authentication, filtering, searching, ordering, and pagination with Djoser and django-filters.

# 1. Project Setup
Create project directory and environment
mkdir littlelemon
cd littlelemon
brew install pipenv
pipenv shell
Install Django
brew install django

# Create Django project and app
django-admin startproject littlelemon .
python3 manage.py startapp littlelemonDRF
Don’t forget to add 'littlelemonDRF' to your INSTALLED_APPS inside settings.py.

# 2. Database Setup
python3 manage.py makemigrations
python3 manage.py migrate

# 3. Run the Server
python3 manage.py runserver

# 4. Install Dependencies
Django REST Framework Setup

1. Install DRF
pip install djangorestframework
Add to INSTALLED_APPS in settings.py:
INSTALLED_APPS = [
...,
'rest_framework',
]

2. Enable XML Renderer
pipenv install djangorestframework-xml
Add the renderer configuration in settings.py:
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [ 'rest_framework.renderers.JSONRenderer','rest_framework.renderers.BrowsableAPIRenderer','rest_framework.renderers.XMLRenderer',
]
}

3. Djoser (User Management + Authentication)
Install Djoser and JWT support:
pip install djoser djangorestframework-simplejwt
Add to INSTALLED_APPS in settings.py:
INSTALLED_APPS = [
    ...,'rest_framework','rest_framework.authtoken','djoser','littlelemonDRF',  # your Django app
]

Configure REST framework with JWT authentication:
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

Add Djoser settings in settings.py:
DJOSER = {
    'USER_ID_FIELD': 'id',
    'LOGIN_FIELD': 'username',
    'SERIALIZERS': {
        'user_create': 'djoser.serializers.UserCreateSerializer',
        'user': 'djoser.serializers.UserSerializer',
        'current_user': 'djoser.serializers.UserSerializer',
    },
}

# Include Djoser URLs in your project-level urls.py:
from django.urls import path, include

urlpatterns = [
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
]

# Create Superuser
python3 manage.py createsuperuser
Example:
Username: seoyeonchoi
Email: seoyeonchoi2001@gmail.com
Password: stella

# 5. Filtering, Searching, and Ordering
Install django-filter
pip install django-filter
Add to INSTALLED_APPS:
INSTALLED_APPS = [
    ...,
    'django_filters',
]
# Add filter settings to REST_FRAMEWORK:
REST_FRAMEWORK = {
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 4,

    # Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '1000/day',
        'anon': '100/day',
    },

    # Filtering, Searching, and Ordering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],

    # Authentication (Browser + Token)
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication', # this is important! 
        'rest_framework.authentication.TokenAuthentication',
    ),
}

# 6. Implement Filtering in Views
Example (views.py):
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    # Enable filtering, searching, and ordering
    filterset_fields = ['title', 'price']
    search_fields = ['title', 'category__title']  # related FK lookup
    ordering_fields = ['title', 'price']

# 7. Testing the API
With Authentication (Bearer Token)
Login first to get your token:
POST /api/token/login/
Body:
{
  "username": "seoyeonchoi",
  "password": "stella"
}
Response:
{"auth_token": "your_token_here"}

# Then in Insomnia or Postman, add:
Authorization: Bearer your_token_here
Filtering, Searching, and Ordering Examples
Feature	Example URL	Description
Filter by field	http://127.0.0.1:8000/api/menu-items/?price=5.50	
Returns items where price = 5.50

Search	http://127.0.0.1:8000/api/menu-items/?search=Ramen	
Finds items with “Ramen” in title or category

Order Ascending	http://127.0.0.1:8000/api/menu-items/?ordering=price	Sorts by price (low → high)

Order Descending	http://127.0.0.1:8000/api/menu-items/?ordering=-price	Sorts by price (high → low)

# 8. Testing from Browser
To test filtering and browsing from the Django REST Framework website:
Visit /admin/ and log in.
Open /api/menu-items/ in a new tab.
The session cookie automatically authenticates you.
You can now use filter, search, and ordering directly in the web interface.

# Now your Little Lemon API is ready with:
User registration & login (Djoser + JWT)
Authenticated API access (Token & Session)
Filtering, searching, and ordering
Pagination & throttling
XML, JSON, and browsable API rendering
