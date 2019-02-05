from django.urls import path

from . import views, glist

urlpatterns = [
    path('', glist.showGsocUser, name='gsoclist'),
    path('refresh', views.github, name='refresh'),
    path('all_list/', views.showAll, name='all_list'),
    path('add_user/<str:user>/', glist.addUser, name='add_user'),
    path('remove_user/<str:user>/', glist.removeUser, name='remove_user'),
]
