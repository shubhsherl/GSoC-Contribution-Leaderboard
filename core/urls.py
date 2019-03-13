from django.urls import path

from . import views

urlpatterns = [
    path('', views.showGsocUser, name='gsoclist'),
]
