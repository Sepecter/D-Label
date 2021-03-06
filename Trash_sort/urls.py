"""Trash_sort URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from server import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'login', views.Login.as_view()),
    path(r'register', views.Register.as_view()),
    path(r'collection', views.Collection.as_view()),
    path(r'photo', views.Photo.as_view()),
    path(r'user_info', views.User_Info.as_view()),
    path(r'predict', views.Predict.as_view()),
    path(r'label', views.Label.as_view()),
    path(r'download', views.Download.as_view()),
]
