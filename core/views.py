# import the logging library
import logging
import json
from django.contrib import messages 
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
import requests
import operator
from github import Github, GithubException
from .models import User, Glist

logger = logging.getLogger(__name__)

def github(request):
    # context = {}
    # contributors = []
    username = 'RocketChat'
    url = 'https://api.github.com/orgs/%s/repos' % username
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
    search_was_successful = (response.status_code == 200)  # 200 = SUCCESS
    search_result = response.json()
    if search_was_successful:
        contributors = getOrganizationContributors(search_result)
    if request.META.get('HTTP_REFERER').split('/')[-2] == 'all_list':
        return HttpResponseRedirect("/all_list/")
    else:
        return HttpResponseRedirect("/")

def getOrganizationContributors(repoList):
    contributors = {}
    for repo in repoList:
        userList = getRepoContributors(repo['owner']['login'], repo['name'])
        for user in userList:
            author = user['author']
            username = author['login']
            commits = user['total']
            add, delete = getadddel(user)
            if username in contributors:
                contributors[username]['commits'] += commits
                contributors[username]['add'] +=add
                contributors[username]['delete'] += delete
                if User.objects.filter(login=username):
                    User.objects.filter(login = username).update(totalCommits = contributors[username]['commits'], totalAdd = contributors[username]['add'], totalDelete = contributors[username]['delete'])
            else:
                contributors[username] = {}
                contributors[username]['commits'] = commits
                contributors[username]['add'] = add
                contributors[username]['delete'] = delete
                contributors[username]['avatar'] = author['avatar_url']
                if not User.objects.filter(login=username):
                    gsoc_aspirant = False
                    if Glist.objects.filter(login=username):
                        gsoc_aspirant = True
                    newUser = User(login = username, avatar = author['avatar_url'], totalCommits = commits, totalAdd = add, totalDelete = delete, gsoc = gsoc_aspirant)
                    newUser.save()
    return contributors

def getRepoContributors(owner, repoName):
    url = 'https://api.github.com/repos/%s/%s/stats/contributors' %(owner, repoName)
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
    return response.json()

def getadddel(user):
    a = 0
    d = 0
    for w in user['weeks']:
        a += w['a']
        d += w['d']
    return a,d


def showAll(request):
    users = User.objects.all().order_by('-totalCommits')
    data = serializers.serialize('json', list(users), fields=('login','id', 'avatar', 'totalCommits', 'gsoc', 'totalAdd', 'totalDelete'))
    context = {
        'users': json.loads(data),
    }
    return render(request, 'core/all_list.html', context)    
