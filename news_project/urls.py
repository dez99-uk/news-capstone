"""Top-level URL configuration for the news project.

This module combines admin, authentication, API, and application routes into a
single root URL configuration.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='news_app/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('api/token/', obtain_auth_token, name='api_token'),
    path('api/', include(('news_app.api_urls', 'news_app_api'), namespace='news_app_api')),
    path('', include(('news_app.urls', 'news_app'), namespace='news_app')),
]
