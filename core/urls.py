from django.urls import path

from . import views, glist

urlpatterns = [
    path('', glist.showGsocUser, name='gsoclist'),
    path('all_list/', views.showAll, name='all_list'),
]
