import json
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.core import serializers
from .models import User, Glist

def showGsocUser(request):
    users = User.objects.filter(gsoc=True).order_by('-totalCommits')
    data = serializers.serialize('json', list(users), fields=('login','id', 'avatar', 'totalCommits', 'totalAdd', 'totalDelete'))
    context = {
        'users': json.loads(data),
    }
    return render(request, 'core/gsoclist.html', context)

def addUser(request, user):
    if User.objects.filter(login=user):
        User.objects.filter(login = user).update(gsoc = True)
        if not Glist.objects.filter(login = user):
            newUser = Glist(login = user)
            newUser.save()
    return HttpResponseRedirect("/all_list/")

def removeUser(request, user):
    if User.objects.filter(login=user):
        User.objects.filter(login = user).update(gsoc = False)
        if Glist.objects.filter(login = user):
            Glist.objects.filter(login = user).delete()
    if request.META.get('HTTP_REFERER').split('/')[-2] == 'all_list':
        return HttpResponseRedirect("/all_list/")
    else:
        return HttpResponseRedirect("/")