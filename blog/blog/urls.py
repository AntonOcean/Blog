"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('backend.urls')),
    # path('auth/', include('knox.urls')),
    path("auth/register/", views.RegistrationAPI.as_view(), name='register'),
    path("auth/login/", views.LoginAPI.as_view(), name='login'),
    path("auth/user/", views.UserAPI.as_view()),
]
