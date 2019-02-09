import json
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
import datetime
import requests
import operator
from github import Github, GithubException
from .models import User, LastUpdate, Repository

AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.BASE_URL
ORG = settings.ORGANIZATION

def github(request):
    search_result = getOrganizationRepositories(ORG)
    if search_result and getOrganizationContributors(search_result):
        if LastUpdate.objects.filter(pk=1):
            LastUpdate.objects.filter(pk=1).update(
                updated=datetime.datetime.now())
        else:
            updated = LastUpdate(pk=1, updated=datetime.datetime.now())
            updated.save()
    return HttpResponseRedirect("/")


def getOrganizationRepositories(org, url=''):
    repositories = []
    if not url:
        url = BASE_URL + 'orgs/%s/repos' % org
    response = requests.get(
        url, headers={'Authorization': 'token ' + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        repositories = response.json()
        if 'next' in response.links:
            repositories += getOrganizationRepositories(
                org, response.links['next']['url'])
    return repositories


def getOrganizationContributors(repoList):
    contributors = {}
    for repo_ in repoList:
        if not Repository.objects.filter(repo=repo_['name']):
            newRepo = Repository(repo=repo_['name'], owner=repo_['owner']['login'])
            newRepo.save()
    repo = Repository.objects.filter(include=True)
    includedRepo = json.loads(serializers.serialize('json', list(repo), fields=('owner','repo')))
    for repo_ in includedRepo:
        owner = repo_['fields']['owner']
        repoName = repo_['fields']['repo']
        userList = getRepoContributors(owner, repoName)
        pullReq = getRepoPR(owner, repoName)
        issues = getRepoIssues(owner, repoName)
        contributors = saveUser(userList, contributors)
        contributors = savePRs(pullReq, contributors)
        contributors = saveIssues(issues, contributors)
    return contributors != {}


def getRepoContributors(owner, repoName, url=''):
    contributors = []
    if not url:
        url = BASE_URL + 'repos/%s/%s/contributors' % (
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
        url = BASE_URL + 'repos/%s/%s/pulls' % (owner, repoName)
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
        url = BASE_URL + 'repos/%s/%s/issues' % (owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        issues = response.json()
        if 'next' in response.links:
            issues += getRepoIssues(owner, repoName,
                                    response.links['next']['url'])
    return issues


def saveUser(userList, contributors):
    for user in userList:
        username = user['login']
        commits = user['contributions']
        if username in contributors:
            contributors[username]['commits'] += commits
            if User.objects.filter(login=username):
                User.objects.filter(login=username).update(
                    totalCommits=contributors[username]['commits'])
        else:
            contributors[username] = {}
            contributors[username]['commits'] = commits
            contributors[username]['PR_counts'] = 0
            contributors[username]['issue_counts'] = 0
            if not User.objects.filter(login=username):
                newUser = User(
                    login=username, avatar=user['avatar_url'], totalCommits=commits)
                newUser.save()
            else:
                User.objects.filter(login=username).update(
                    totalCommits=contributors[username]['commits'])
    return contributors


def savePRs(pullReq, contributors_):
    contributors = contributors_
    for pull in pullReq:
        if 'open' == pull['state']:
            username = pull['user']['login']
            if username in contributors:
                contributors[username]['PR_counts'] += 1
                if User.objects.filter(login=username):
                    User.objects.filter(login=username).update(
                        totalPRs=contributors[username]['PR_counts'])
            else:
                contributors[username] = {}
                contributors[username]['PR_counts'] = 1
                contributors[username]['issue_counts'] = 0
                contributors[username]['commits'] = 0
                if User.objects.filter(login=username):
                    User.objects.filter(login=username).update(
                        totalPRs=contributors[username]['PR_counts'])
                else:
                    newUser = User(
                        login=username, avatar=pull['user']['avatar_url'], totalPRs=contributors[username]['PR_counts'])
                    newUser.save()
    return contributors


def saveIssues(issues, contributors_):
    contributors = contributors_
    for issue in issues:
        if True:
            username = issue['user']['login']
            if username in contributors:
                contributors[username]['issue_counts'] += 1
                if User.objects.filter(login=username):
                    User.objects.filter(login=username).update(
                        totalIssues=contributors[username]['issue_counts'])
            else:
                contributors[username] = {}
                contributors[username]['issue_counts'] = 1
                contributors[username]['PR_counts'] = 0
                contributors[username]['commits'] = 0
                if User.objects.filter(login=username):
                    User.objects.filter(login=username).update(
                        totalIssues=contributors[username]['issue_counts'])
                else:
                    newUser = User(
                        login=username, avatar=issue['user']['avatar_url'], totalIssues=contributors[username]['issue_counts'])
                    newUser.save()
    return contributors


def showAll(request):
    sort = 'c'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    if LastUpdate.objects.filter(pk=1):
        lastUpdated = LastUpdate.objects.get(pk=1).updated
    else:
        lastUpdated = ''    
    users = sortUser(User.objects.all(), sort)
    data = serializers.serialize('json', list(users), fields=(
        'login', 'id', 'avatar', 'totalCommits', 'gsoc', 'totalPRs', 'totalIssues'))
    context = {
        'users': json.loads(data),
        'updated': lastUpdated,
    }
    return render(request, 'core/all_list.html', context)


def sortUser(User, key):
    if key == 'c':
        return User.order_by('-totalCommits')
    if key == 'p':
        return User.order_by('-totalPRs')
    if key == 'i':
        return User.order_by('-totalIssues')
