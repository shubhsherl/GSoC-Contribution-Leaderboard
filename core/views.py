import json
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
import datetime
import requests

from .models import User, LastUpdate, Repository, Relation
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
    if response.status_code == 200:  # 200 = SUCCESS
        repositories = response.json()
        if 'next' in response.links:
            repositories += getOrganizationRepositories(
                org, response.links['next']['url'])
    return repositories


def getOrganizationContributors(repoList):
    repos = {}
    changed_repos = []
    gsoc_users = list(User.objects.filter(gsoc=True).values_list('login', flat=True))

    for repo_ in repoList:
        currRepo, created = Repository.objects.get_or_create(repo=repo_['name'],
                                                             defaults={
                                                                 'owner': repo_['owner']['login'],
                                                                 'openIssues': -1,
                                                                 'gsoc': False
                                                             }
                                                             )
        if not created:
            if currRepo.openIssues != repo_['open_issues'] and currRepo.gsoc:
                currRepo.openIssues = repo_['open_issues']
                currRepo.save()
                changed_repos.append(currRepo)

        changed_repos_json = json.loads(serializers.serialize('json', changed_repos, fields=('owner', 'repo')))

    for repo_ in changed_repos_json:
        contributors = {}
        owner = repo_['fields']['owner']
        repo_name = repo_['fields']['repo']
        contributors = getRepoIssues(owner, repo_name, contributors, gsoc_users)
        contributors = getRepoPR(owner, repo_name, contributors, gsoc_users)
        contributors = getRepoContributors(owner, repo_name, contributors, gsoc_users)
        repos[repo_name] = contributors

    updateDataBase(repos)

    return repos != {}


# TODO make refactor to this function
def updateDataBase(repos):
    for repo_ in repos:
        print(repo_ + "->" + str(datetime.datetime.now()))
        curreRepo = Repository.objects.get(repo=repo_)
        for user in repos[repo_]:
            currUser = User.objects.get(login=user)
            currRelation, created = Relation.objects.get_or_create(repo=curreRepo, user=currUser,
                                                                   defaults={
                                                                       'user': currUser,
                                                                       'repo': curreRepo,
                                                                       'totalOpenPRs': repos[repo_][user]['open_prs'],
                                                                       'totalMergedPRs': repos[repo_][user][
                                                                           'merged_prs'],
                                                                       'totalIssues': repos[repo_][user]['issue_counts']

                                                                   })
            if not created:
                currRelation.totalOpenPRs = repos[repo_][user]['open_prs']
                currRelation.totalMergedPRs = repos[repo_][user]['merged_prs']
                currRelation.totalIssues = repos[repo_][user]['issue_counts']
                currRelation.save()

    print('finish update database' + "->" + str(datetime.datetime.now()))


def getRepoContributors(owner, repoName, contributors_, gsoc_list, url=''):
    contributors = contributors_
    if not url:
        url = BASE_URL + 'repos/%s/%s/contributors?per_page=100' % (
            owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if response.status_code == 200:  # 200 = SUCCESS
        users = response.json()
        saveUser(users, contributors_, gsoc_list)
        if 'next' in response.links:
            contributors = getRepoContributors(owner,
                                               repoName,
                                               contributors_,
                                               gsoc_list,
                                               response.links['next']['url'])
    return contributors


def getRepoPR(owner, repoName, contributors_, gsoc_list, url=''):
    contributors = contributors_
    if not url:
        url = BASE_URL + 'repos/%s/%s/pulls?per_page=100' % (owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if response.status_code == 200:  # 200 = SUCCESS
        pulls = response.json()
        savePRs(pulls, contributors, gsoc_list)
        if 'next' in response.links:
            contributors = getRepoPR(owner,
                                     repoName,
                                     contributors,
                                     gsoc_list,
                                     response.links['next']['url'])
    return contributors


def getRepoIssues(owner, repoName, contributors_, gsoc_list, url=''):
    contributors = contributors_
    if not url:
        url = BASE_URL + 'repos/%s/%s/issues?per_page=100' % (owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if response.status_code == 200:  # 200 = SUCCESS
        issues = response.json()
        saveIssues(issues, contributors, gsoc_list)
        if 'next' in response.links:
            getRepoIssues(owner,
                          repoName,
                          contributors,
                          gsoc_list,
                          response.links['next']['url'])
    return contributors


def saveUser(userList, contributors, gsoc_list):
    for user in userList:
        username = user['login'].lower()
        merged_prs = user['contributions']
        if username in gsoc_list:
            if username in contributors:
                contributors[username]['merged_prs'] += merged_prs
            else:
                contributors[username] = {}
                contributors[username]['merged_prs'] = merged_prs
                contributors[username]['open_prs'] = 0
                contributors[username]['issue_counts'] = 0
                contributors[username]['avatar_url'] = user['avatar_url']
    return contributors


def savePRs(pullReq, contributors_, gsoc_list):
    contributors = contributors_
    for pull in pullReq:
        if 'open' == pull['state']:
            username = pull['user']['login'].lower()
            if username in gsoc_list:
                if username in contributors:
                    contributors[username]['open_prs'] += 1
                else:
                    contributors[username] = {}
                    contributors[username]['open_prs'] = 1
                    contributors[username]['issue_counts'] = 0
                    contributors[username]['merged_prs'] = 0
                    contributors[username]['avatar_url'] = pull['user']['avatar_url']

    return contributors


def saveIssues(issues, contributors_, gsoc_list):
    contributors = contributors_
    for issue in issues:
        username = issue['user']['login'].lower()
        if username in gsoc_list:
            if username in contributors:
                contributors[username]['issue_counts'] += 1
            else:
                contributors[username] = {}
                contributors[username]['issue_counts'] = 1
                contributors[username]['open_prs'] = 0
                contributors[username]['merged_prs'] = 0

    return contributors


def showGsocUser(request):
    sort = 'd'
    if 'sort' in request.GET:
        sort = request.GET['sort']
    if LastUpdate.objects.filter(pk=1):
        lastUpdated = LastUpdate.objects.get(pk=1).updated
    else:
        lastUpdated = ''
    data = sortUser(Relation.objects, sort)

    context = {
        'users': data,
        'updated': lastUpdated,
    }
    return render(request, 'core/gsoclist.html', context)


def sortUser(_User, key):
    all_list = _User.filter(user__gsoc=True).extra(select={'count': 'totalOpenPRs + totalMergedPRs'}).values(
        'user__login', 'user__id', 'user__avatar',
        'user__gsoc').annotate(Sum('totalIssues'),
                               Sum('totalOpenPRs'),
                               Sum('totalMergedPRs'))
    if key == 'i':
        return all_list.order_by('-totalIssues__sum')
    if key == 'p':
        return all_list.order_by('-totalOpenPRs__sum')
    if key == 'c':
        return all_list.order_by('-totalMergedPRs__sum')
    # defalut case for gsoc
    return all_list.order_by('-count', )
