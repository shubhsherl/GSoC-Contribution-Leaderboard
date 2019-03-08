import json
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
import datetime
import time
import requests
from .models import User, LastUpdate, Repository

AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.API_BASE_URL
ORG = settings.ORGANIZATION

def github():
    search_result = getOrganizationRepositories()
    if search_result and getOrganizationContributors(search_result):
        if LastUpdate.objects.filter(pk=1):
            LastUpdate.objects.filter(pk=1).update(
                allList=datetime.datetime.now())
        else:
            updated = LastUpdate(pk=1, allList=datetime.datetime.now())
            updated.save()
    return

def gsoc():
    success = False
    user = User.objects.filter(gsoc=True)
    gsoclist = json.loads(serializers.serialize('json', list(user), fields=('login')))
    for user in gsoclist:
        username = user['fields']['login']
        success = getOpenPRs(username) and getMergedPRs(username) and getIssues(username)
    if success:
        if LastUpdate.objects.filter(pk=1):
            LastUpdate.objects.filter(pk=1).update(
                gList=datetime.datetime.now())
        else:
            updated = LastUpdate(pk=1, gList=datetime.datetime.now())
            updated.save()

def getOrganizationRepositories(url=''):
    repositories = []
    if not url:
        url = BASE_URL + 'orgs/%s/repos?per_page=100' % ORG
    response = requests.get(
        url, headers={'Authorization': 'token ' + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        repositories = response.json()
        if 'next' in response.links:
            repositories += getOrganizationRepositories(response.links['next']['url'])
    return repositories


def getOrganizationContributors(repoList):
    contributors = {}
    for repo_ in repoList:
        if not Repository.objects.filter(repo=repo_['name']):
            newRepo = Repository(repo=repo_['name'], owner=repo_['owner']['login'], include=False)
            newRepo.save()
    repo = Repository.objects.filter(include=True)
    includedRepo = json.loads(serializers.serialize('json', list(repo), fields=('owner','repo')))
    for repo_ in includedRepo:
        owner = repo_['fields']['owner']
        repoName = repo_['fields']['repo']
        userList = getRepoContributors(owner, repoName)
        pullReq = getRepoPR(owner, repoName)
        issues = getRepoIssues(owner, repoName)
        contributors = saveUser(userList, pullReq, issues, contributors)
    return contributors != {}


def getRepoContributors(owner, repoName, url=''):
    contributors = []
    if not url:
        url = BASE_URL + 'repos/%s/%s/contributors?per_page=100' % (
            owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        contributors = response.json()
        if 'next' in response.links:
            contributors += getRepoContributors(owner,
                                                repoName, response.links['next']['url'])
    return contributors


def getRepoPR(owner, repoName, url=''):
    pulls = []
    if not url:
        url = BASE_URL + 'repos/%s/%s/pulls?per_page=100' % (owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        pulls = response.json()
        if 'next' in response.links:
            pulls += getRepoPR(owner, repoName, response.links['next']['url'])
    return pulls


def getRepoIssues(owner, repoName, url=''):
    issues = []
    if not url:
        url = BASE_URL + 'repos/%s/%s/issues?per_page=100' % (owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        issues = response.json()
        if 'next' in response.links:
            issues += getRepoIssues(owner, repoName,
                                    response.links['next']['url'])
    return issues

def saveUser(userList, pullReq, issues, contributors):
    for user in userList:
        username = user['login'].lower()
        if not username in contributors:
            contributors[username] = {}
            contributors[username]['updated'] = True
            if not User.objects.filter(login=username):
                newUser = User(login=username, avatar=user['avatar_url'])
                newUser.save()
            update(username)
    for pull in pullReq:
        username = pull['user']['login'].lower()
        if not username in contributors:
            contributors[username] = {}
            contributors[username]['updated'] = True
            if not User.objects.filter(login=username):
                newUser = User(login=username, avatar=user['avatar_url'])
                newUser.save()
            update(username)
    for issue in issues:
        username = issue['user']['login'].lower()
        if not username in contributors:
            contributors[username] = {}
            contributors[username]['updated'] = True
            if not User.objects.filter(login=username):
                newUser = User(login=username, avatar=user['avatar_url'])
                newUser.save()
            update(username)
    return contributors

def update(username):
    getMergedPRs(username)
    getIssues(username)
    getOpenPRs(username)

def getMergedPRs(username):
    mergedPRs = -1
    url = BASE_URL + 'search/issues?q=org:%s+author:%s+archived:false+is:merged+is:pr' % (ORG, username)
    response = requests.get(url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200): #success
        mergedPRs = response.json()['total_count']
        if User.objects.filter(login=username):
            User.objects.filter(login=username).update(totalMergedPRs=mergedPRs)
    elif (response.status_code == 403): # rate-limit exceeded wait for 30sec 
        time.sleep(30)
        getMergedPRs(username)        
    return mergedPRs != -1

def getIssues(username):
    issues = -1
    url = BASE_URL + 'search/issues?q=org:%s+author:%s+archived:false+is:issue' % (ORG, username)
    response = requests.get(url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):
        issues = response.json()['total_count']
        if User.objects.filter(login=username):
            User.objects.filter(login=username).update(totalIssues=issues)
    elif (response.status_code == 403):
        time.sleep(30)
        getIssues(username)
    return issues != -1

def getOpenPRs(username):
    openPRs = -1
    url = BASE_URL + 'search/issues?q=org:%s+author:%s+archived:false+is:open+is:pr' % (ORG, username)
    response = requests.get(url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):
        openPRs = response.json()['total_count']
        if User.objects.filter(login=username):
            User.objects.filter(login=username).update(totalOpenPRs=openPRs)
    elif (response.status_code == 403):
        time.sleep(30)
        getOpenPRs(username)
    return openPRs != -1


def showAll(request):
    sort = 'd'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    if LastUpdate.objects.filter(pk=1):
        lastUpdated = LastUpdate.objects.get(pk=1).allList
    else:
        lastUpdated = ''
    users = sortUser(User.objects.all(), sort)

    data = serializers.serialize('json', list(users), fields=(
        'login', 'id', 'avatar', 'totalMergedPRs', 'gsoc', 'totalOpenPRs', 'totalIssues'))
    context = {
        'users': json.loads(data),
        'updated': lastUpdated,
    }
    return render(request, 'core/all_list.html', context)


def sortUser(_User, key, _gsoc = False):
    if key == 'm':
        return _User.order_by('-totalMergedPRs')
    if key == 'p':
        return _User.order_by('-totalOpenPRs')
    if key == 'i':
        return _User.order_by('-totalIssues')
    if _gsoc: # defalut case for gsoc
        return User.objects.filter(gsoc=_gsoc).extra(
        select={'count':'totalMergedPRs + totalOpenPRs + totalIssues'},
        order_by=('-count',),
        )
    else: # default case for all
        return User.objects.extra(
        select={'count':'totalMergedPRs + totalOpenPRs + totalIssues'},
        order_by=('-count',),
        )
