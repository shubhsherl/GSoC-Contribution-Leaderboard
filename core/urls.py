from django.urls import path

from . import views

urlpatterns = [
    path('', views.github, name='github'),
    path('gsoclist/', views.showUser, name='gsoclist'),
    path('all_list/', views.showAll, name='all_list'),
    path('add_user/', views.addUser, name='add_user'),
    path('remove_user/', views.removeUser, name='remove_user'),
    path('ajax/load_users/', views.loadUsers, name='load_users'),
]
