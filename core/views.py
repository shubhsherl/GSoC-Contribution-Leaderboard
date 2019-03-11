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
from .models import User, LastUpdate, Repository ,Relation
from django.db.models import Sum


AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.API_BASE_URL
ORG = settings.ORGANIZATION

def github():
    search_result = getOrganizationRepositories(ORG)
    if search_result and getOrganizationContributors(search_result):
        if LastUpdate.objects.filter(pk=1):
            LastUpdate.objects.filter(pk=1).update(
                updated=datetime.datetime.now())
        else:
            updated = LastUpdate(pk=1, updated=datetime.datetime.now())
            updated.save()
    return


def getOrganizationRepositories(org, url=''):
    repositories = []
    if not url:
        url = BASE_URL + 'orgs/%s/repos?per_page=100' % org
    response = requests.get(
        url, headers={'Authorization': 'token ' + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        repositories = response.json()
        if 'next' in response.links:
            repositories += getOrganizationRepositories(
                org, response.links['next']['url'])
    return repositories


def getOrganizationContributors(repoList):

    repos={}
    issueRepos=[]
    for repo_ in repoList:
        currRepo=Repository.objects.filter(repo=repo_['name'])
        if not currRepo:
            newRepo = Repository(repo=repo_['name'], owner=repo_['owner']['login'],openIssues=repo_['open_issues'], include=False)
            newRepo.save()
            issueRepos+=Repository.objects.filter(repo=repo_['name'],include=True)
        else :
           if currRepo[0].openIssues!= repo_['open_issues']and currRepo[0].include:
               currRepo.update(openIssues=repo_['open_issues'])
               issueRepos +=currRepo


    forIssues =json.loads(serializers.serialize('json', list(issueRepos), fields=('owner','repo')))
    for repo_ in forIssues:
        contributors = {}
        owner = repo_['fields']['owner']
        repoName = repo_['fields']['repo']
        contributors = getRepoIssues(owner, repoName, contributors)
        contributors = getRepoPR(owner, repoName, contributors)
        contributors = getRepoContributors(owner, repoName, contributors)
        repos[repoName]=contributors

    updateDataBase(repos)

        # contributors = saveUser(userList, contributors)
        # contributors = savePRs(pullReq, contributors)
        # contributors = saveIssues(issues, contributors)

    return contributors != {}

#TODO make refactor to this function
def updateDataBase(repos):
    for repo_ in repos:
        for user in repos[repo_]:
            currUser = User.objects.filter(login=user)
            curreRepo=Repository.objects.get(repo=repo_)
            if currUser:
              currRelation=Relation.objects.filter(repo= curreRepo ,user =currUser[0])
              if currRelation:
                  currRelation.update(totalPRs=repos[repo_][user]['PR_counts'],
                                     totalCommits=repos[repo_][user]['commits'],
                                    totalIssues = repos[repo_][user]['issue_counts']
                                      )
              else:
                  newRelation=Relation(
                      user=currUser[0],
                      repo= curreRepo,
                      totalPRs=repos[repo_][user]['PR_counts'],
                      totalCommits=repos[repo_][user]['commits'],
                      totalIssues=repos[repo_][user]['issue_counts']
                  )
                  newRelation.save()
            else:
                newUser = User(
                    login=user,
                    avatar=repos[repo_][user]['avatar_url']
                )
                newUser.save()
                newRelation = Relation(
                    user=newUser,
                    repo=curreRepo,
                    totalPRs=repos[repo_][user]['PR_counts'],
                    totalCommits=repos[repo_][user]['commits'],
                    totalIssues=repos[repo_][user]['issue_counts']
                )
                newRelation.save()





def getRepoContributors(owner, repoName,contributors_, url=''):
    contributors = contributors_
    if not url:
        url = BASE_URL + 'repos/%s/%s/contributors?per_page=100' % (
            owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        users = response.json()
        saveUser(users, contributors)
        if 'next' in response.links:
            contributors = getRepoContributors(owner,
                                                repoName,
                                                contributors_,
                                                response.links['next']['url'])
    return contributors


def getRepoPR(owner, repoName, contributors_, url=''):
    contributors = contributors_
    if not url:
        url = BASE_URL + 'repos/%s/%s/pulls?per_page=100' % (owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        pulls = response.json()
        savePRs(pulls, contributors)
        if 'next' in response.links:
            contributors = getRepoPR(owner, repoName,contributors, response.links['next']['url'])
    return contributors


def getRepoIssues(owner, repoName, contributors_, url=''):
    contributors = contributors_
    if not url:
        url = BASE_URL + 'repos/%s/%s/issues?per_page=100' % (owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        issues = response.json()

        saveIssues(issues, contributors)
        if 'next' in response.links:
            getRepoIssues(owner,
                          repoName,
                          contributors,
                          response.links['next']['url'])
    return contributors


def saveUser(userList, contributors):
    for user in userList:
        username = user['login'].lower()
        commits = user['contributions']
        if username in contributors:
            contributors[username]['commits'] += commits
        else:
            contributors[username] = {}
            contributors[username]['commits'] = commits
            contributors[username]['PR_counts'] = 0
            contributors[username]['issue_counts'] = 0
            contributors[username]['avatar_url'] = user['avatar_url']
    return contributors


def savePRs(pullReq, contributors_):
    contributors = contributors_
    for pull in pullReq:
        if 'open' == pull['state']:
            username = pull['user']['login'].lower()
            if username in contributors:
                contributors[username]['PR_counts'] += 1
            else:
                contributors[username] = {}
                contributors[username]['PR_counts'] = 1
                contributors[username]['issue_counts'] = 0
                contributors[username]['commits'] = 0
                contributors[username]['avatar_url'] = pull['user']['avatar_url']

    return contributors


def saveIssues(issues, contributors_):
    contributors = contributors_
    for issue in issues:
            username = issue['user']['login'].lower()
            if username in contributors:
                contributors[username]['issue_counts'] += 1
            else:
                contributors[username] = {}
                contributors[username]['issue_counts'] = 1
                contributors[username]['PR_counts'] = 0
                contributors[username]['commits'] = 0
                contributors[username]['avatar_url'] = issue['user']['avatar_url']

    return contributors


def showAll(request):
    sort = 'd'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    if LastUpdate.objects.filter(pk=1):
        lastUpdated = LastUpdate.objects.get(pk=1).updated
    else:
        lastUpdated = ''

    data = sortUser(
        Relation.objects,
        sort)


    context = {
        'users': data,
        'updated': lastUpdated,
    }
    return render(request, 'core/all_list.html', context)


def sortUser(_User, key, _gsoc = False):
    if(_gsoc):
        all_list=_User.filter(user__gsoc=_gsoc).values('user__login', 'user__id', 'user__avatar', 'user__gsoc').annotate(Sum('totalIssues'),
                                                                             Sum('totalPRs'),
                                                                             Sum('totalCommits'))
    else :
        all_list = _User.values('user__login', 'user__id', 'user__avatar',
                                                         'user__gsoc').annotate(Sum('totalIssues'),
                                                                                Sum('totalPRs'),
                                                                                Sum('totalCommits'))
    if key == 'i':
        return all_list.order_by('-totalIssues__sum')
    if key == 'p':
        return all_list.order_by('-totalPRs__sum')
    if key == 'c':
        return all_list.order_by('-totalCommits__sum')
    if _gsoc: #defalut case for gsoc
        return all_list
    else: #default case for all
        return list(all_list)
