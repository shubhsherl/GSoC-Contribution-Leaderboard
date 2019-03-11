from django.urls import path

from . import views, glist

urlpatterns = [
    path('', glist.showGsocUser, name='gsoclist'),
]
