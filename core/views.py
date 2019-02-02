# import the logging library
import logging
import json
from django.contrib import messages 
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
import requests
import operator
from github import Github, GithubException
from .models import User, Glist
from .forms import GlistForm


# Get an instance of a logger
logger = logging.getLogger(__name__)

def github(request):
    context = {}
    contributors = []
    # search_was_successful = False
    if 'username' in request.GET:
        username = request.GET['username']
        url = 'https://api.github.com/orgs/%s/repos' % username
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
        search_was_successful = (response.status_code == 200)  # 200 = SUCCESS
        search_result = response.json()
        if search_was_successful:
            contributors = getOrganizationContributors(search_result)
        search_result = sorted(contributors.items(), key=lambda x: x[1]['commits'] ,reverse=True)
        # search_result['success'] = search_was_successful
        # search_result['rate'] = {
        #     'limit': response.headers['X-RateLimit-Limit'],
        #     'remaining': response.headers['X-RateLimit-Remaining'],
        # }
        context = {
            'search_result': search_result,
            'search_was_successful': search_was_successful, 
            'contributors': contributors
            }
    return render(request, 'core/github.html', context)

def getOrganizationContributors(repoList):
    contributors = {}
    for repo in repoList:
        # contributors.extend(getRepoContributors(repo))
        userList = getRepoContributors(repo)
        for user in userList:
            if user['login'] in contributors:
                contributors[user['login']]['commits'] += user['contributions']
                if User.objects.filter(login=user['login']):
                    User.objects.filter(login = user['login']).update(totalCommits = contributors[user['login']]['commits'])
            else:
                contributors[user['login']] = {}
                contributors[user['login']]['commits'] = user['contributions']
                contributors[user['login']]['avatar'] = user['avatar_url']
                contributors[user['login']]['avatar'] = user['avatar_url']
                if not User.objects.filter(login=user['login']):
                    newUser = User(login = user['login'], avatar = user['avatar_url'], totalCommits = user['contributions'])
                    newUser.save()
    return contributors

def getRepoContributors(repo):
    url = 'https://api.github.com/repos/%s/%s/contributors' %(repo['owner']['login'], repo['name'])
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
    return response.json()  


def showUser(request):
    form = GlistForm(request.POST or None)
    data = {}
    if form.is_valid():
        user = form.cleaned_data['login']
        if User.objects.filter(login=user):
            User.objects.filter(login = user).update(gsoc = True)
            newUser = Glist(login = user)
            newUser.save()
    else:
        messages.info(request, form.errors.as_json())
    users = User.objects.filter(gsoc=True).order_by('-totalCommits')
    data = serializers.serialize('json', list(users), fields=('login','id', 'avatar', 'totalCommits'))
    context = {
        'users': json.loads(data),
        'log': form.errors.as_json(),
    }
    return render(request, 'core/gsoclist.html', context)

def showAll(request):
    users = User.objects.all().order_by('-totalCommits')
    data = serializers.serialize('json', list(users), fields=('login','id', 'avatar', 'totalCommits'))
    context = {
        'users': json.loads(data),
    }
    return render(request, 'core/all_list.html', context)    


def addUser(request):
    form = GlistForm(request.POST or None)
    context = {
        'form': form,
    }
    return render(request, "core/userForm.html", context)

def removeUser(request):
    form = GlistForm(request.POST or None)
    context = {
        'form': form,
    }
    return render(request, "core/userForm.html", context)

def loadUsers(request):
    users = User.objects.all().order_by('login')
    data = serializers.serialize('json', list(users), fields=('login','id', 'avatar', 'totalCommits'))
    context = {'users': json.loads(data)}
    return render(request, 'core/dropdown_list_options.html', context)