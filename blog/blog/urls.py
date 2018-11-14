from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import path, include

from backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('backend.urls')),

    path("register/", views.RegistrationAPI.as_view(), name='register'),
    path("auth/login/", views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('debug_logout/', LogoutView.as_view(next_page='/'), name='debug_logout'),
]
