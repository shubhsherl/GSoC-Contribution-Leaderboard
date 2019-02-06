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
    username = 'RocketChat'
    url = 'https://api.github.com/orgs/%s/repos' % username
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
    search_was_successful = (response.status_code == 200)  # 200 = SUCCESS
    search_result = response.json()
    if search_was_successful:
        getOrganizationContributors(search_result)
    if request.META.get('HTTP_REFERER').split('/')[-2] == 'all_list':
        return HttpResponseRedirect("/all_list/")
    else:
        return HttpResponseRedirect("/")

def getOrganizationContributors(repoList):
    for repo in repoList:
        userList = getRepoContributors(repo['owner']['login'], repo['name'])
        pullReq = getRepoPR(repo['owner']['login'], repo['name'])
        issues = getRepoIssues(repo['owner']['login'], repo['name'])
        contributors = saveUser(userList) # 1
        contributors = savePRs(pullReq, contributors) # 2
        contributors = saveIssues(issues, contributors) # 3

def getRepoContributors(owner, repoName):
    url = 'https://api.github.com/repos/%s/%s/stats/contributors' %(owner, repoName)
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
    return response.json()

def getRepoPR(owner, repoName):
    url = 'https://api.github.com/repos/%s/%s/pulls' %(owner, repoName)
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
    return response.json()

def getRepoIssues(owner, repoName):
    url = 'https://api.github.com/repos/%s/%s/issues' %(owner, repoName)
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
    return response.json()

def saveUser(userList):
    contributors = {}
    for user in userList:
        author = user['author']
        username = author['login']
        commits = user['total']
        add, delete = getadddel(user)
        if username in contributors:
            contributors[username]['commits'] += commits
            contributors[username]['add'] += add
            contributors[username]['delete'] += delete
            if User.objects.filter(login=username):
                User.objects.filter(login = username).update(totalCommits = contributors[username]['commits'], totalAdd = contributors[username]['add'], totalDelete = contributors[username]['delete'])
        else:
            contributors[username] = {}
            contributors[username]['commits'] = commits
            contributors[username]['add'] = add
            contributors[username]['delete'] = delete
            contributors[username]['PR_counts'] = 0
            contributors[username]['issue_counts'] = 0
            if not User.objects.filter(login=username):
                gsoc_aspirant = False
                if Glist.objects.filter(login=username):
                    gsoc_aspirant = True
                newUser = User(login = username, avatar = author['avatar_url'], totalCommits = commits, totalAdd = add, totalDelete = delete, gsoc = gsoc_aspirant)
                newUser.save()
    return contributors

def savePRs(pullReq, contributors_):
    contributors = contributors_
    for pull in pullReq:
        if 'open' == pull['state']:
            username = pull['user']['login']
            if username in contributors:
                contributors[username]['PR_counts'] += 1
                if User.objects.filter(login=username):
                    User.objects.filter(login = username).update(totalPRs = contributors[username]['PR_counts'])
            else:
                contributors[username] = {}
                contributors[username]['PR_counts'] = 1
                contributors[username]['issue_counts'] = 0
                if User.objects.filter(login=username):
                    User.objects.filter(login = username).update(totalPRs = contributors[username]['PR_counts'])
    return contributors                

def saveIssues(issues, contributors_):
    contributors = contributors_
    for issue in issues:
        if True:
            username = issue['user']['login']
            if username in contributors:
                contributors[username]['issue_counts'] += 1
                if User.objects.filter(login=username):
                    User.objects.filter(login = username).update(totalIssues = contributors[username]['issue_counts'])
            else:
                contributors[username] = {}
                contributors[username]['issue_counts'] = 1
                if User.objects.filter(login=username):
                    User.objects.filter(login = username).update(totalIssues = contributors[username]['issue_counts'])
    return contributors
                   

def getadddel(user):
    a = 0
    d = 0
    for w in user['weeks']:
        a += w['a']
        d += w['d']
    return a,d


def showAll(request):
    sort = 'c'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    users = sortUser(User.objects.all(), sort)
    data = serializers.serialize('json', list(users), fields=('login','id', 'avatar', 'totalCommits', 'gsoc', 'totalAdd', 'totalDelete', 'totalPRs', 'totalIssues'))
    context = {
        'users': json.loads(data),
    }
    return render(request, 'core/all_list.html', context)    

def sortUser(User, key):
    if key == 'c':
        return User.order_by('-totalCommits')
    if key == 'a':
        return User.order_by('-totalAdd')
    if key == 'd':
        return User.order_by('-totalDelete')
    if key == 'p':
        return User.order_by('-totalPRs')
    if key == 'i':
        return User.order_by('-totalIssues')    
