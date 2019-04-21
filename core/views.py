import json
from django.shortcuts import render
from django.conf import settings
from datetime import datetime
import requests
from .models import User, LastUpdate, Repository, Relation
from django.db.models import Sum

AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.API_BASE_URL
ORG = settings.ORGANIZATION
SORT = settings.DEFAULT_SORT
SHOW_RANK = settings.SHOW_RANK


def github():
    search_result = getOrganizationRepositories(ORG)
    if search_result and getOrganizationContributors(search_result):
        if LastUpdate.objects.filter(pk=1):
            LastUpdate.objects.filter(pk=1).update(
                updated=datetime.now())
        else:
            updated = LastUpdate(pk=1, updated=datetime.now())
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
    repoTotalIssues = -1
    users = Relation.objects.get_dict()
    for repo_ in repoList:
        currRepo, created = Repository.objects.get_or_create(repo=repo_['name'],
                                                             defaults={'owner': repo_['owner']['login'], 'openIssues': -1, 'totalIssues': -1, 'gsoc': False,
                                                                       })
        if currRepo.gsoc:
            repoTotalIssues = getRepoTotalIssueCount(repo_)
        if currRepo.gsoc and (currRepo.totalIssues != repoTotalIssues or currRepo.openIssues != repo_['open_issues']):
            new_added = (currRepo.totalIssues == -1)
            n = repoTotalIssues - currRepo.totalIssues
            if n <= 0:
                n = 50
            currRepo.openIssues = repo_['open_issues']
            currRepo.totalIssues = repoTotalIssues
            currRepo.save()
            changed_repos.append(
                [currRepo, {'new_added': new_added, 'number': n, }])

    for repo in changed_repos:
        repo_ = repo[0]
        new_added = repo[1]['new_added']
        number = repo[1]['number']
        updated_at = repo_.updatedAt.replace(tzinfo=None)
        updated_at = updated_at.strftime("%Y-%m-%dT%H:%M:%SZ")
        contributors = {}
        owner = repo_.owner
        repo_name = repo_.repo
        contributors, updated_prs = getRepoIssues(
            owner, repo_name, contributors, users, number, new_added, updated_at)
        contributors = getRepoPR(
            owner, repo_name, contributors, users, new_added, updated_prs)
        repos[repo_name] = contributors

    updateDataBase(repos)

    return repoTotalIssues != -1


# TODO make refactor to this function
def updateDataBase(repos):
    for repo_ in repos:
        curreRepo = Repository.objects.get(repo=repo_)
        for user in repos[repo_]:
            currUser = User.objects.get_or_create(
                login=user, defaults={'avatar': repos[repo_][user]['avatar_url']})
            currRelation, created = Relation.objects.get_or_create(
                repo=curreRepo, user=currUser[0])
            if created:
                currRelation.totalOpenPRs = repos[repo_][user]['open_prs']
                currRelation.totalMergedPRs = repos[repo_][user]['merged_prs']
                currRelation.totalIssues = repos[repo_][user]['issue_counts']
                if repos[repo_][user]['last_merged_pr'] is not None:
                    currRelation.lastMergedPR = repos[repo_][user]['last_merged_pr']
                if repos[repo_][user]['last_closed_pr'] is not None:
                    currRelation.lastClosedPR = repos[repo_][user]['last_closed_pr']
                if repos[repo_][user]['last_open_pr'] is not None:
                    currRelation.lastOpenPR = repos[repo_][user]['last_open_pr']
                if repos[repo_][user]['last_issue'] is not None:
                    currRelation.lastIssue = repos[repo_][user]['last_issue']
                currRelation.save()
            else:
                currRelation.totalOpenPRs = currRelation.totalOpenPRs + \
                    repos[repo_][user]['open_prs'] - \
                    repos[repo_][user]['merged_prs'] - \
                    repos[repo_][user]['closed_prs']
                currRelation.totalMergedPRs = currRelation.totalMergedPRs + \
                    repos[repo_][user]['merged_prs']
                currRelation.totalIssues = currRelation.totalIssues + \
                    repos[repo_][user]['issue_counts']
                if repos[repo_][user]['last_merged_pr'] is not None:
                    currRelation.lastMergedPR = repos[repo_][user]['last_merged_pr']
                if repos[repo_][user]['last_closed_pr'] is not None:
                    currRelation.lastClosedPR = repos[repo_][user]['last_closed_pr']
                if repos[repo_][user]['last_open_pr'] is not None:
                    currRelation.lastOpenPR = repos[repo_][user]['last_open_pr']
                if repos[repo_][user]['last_issue'] is not None:
                    currRelation.lastIssue = repos[repo_][user]['last_issue']
                currRelation.save()


def getRepoPR(owner, repoName, contributors_, users, new_added, updated_prs, url=''):
    contributors = contributors_
    if not url:
        if new_added:
            url = BASE_URL + \
                'repos/%s/%s/pulls?per_page=100&state=all' % (owner, repoName)
        else:
            url = BASE_URL + \
                'repos/%s/%s/pulls?sort=updated&per_page=%d&state=all&direction=desc' % (
                    owner, repoName, updated_prs)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if response.status_code == 200:  # 200 = SUCCESS
        pulls = response.json()
        savePRs(repoName, pulls, contributors, users, new_added)
        if 'next' in response.links and new_added:
            contributors = getRepoPR(
                owner, repoName, contributors, users, new_added, updated_prs, response.links['next']['url'])
    return contributors


def getRepoIssues(owner, repoName, contributors_, users, number, new_added, last_updated_at, url=''):
    contributors = contributors_
    updated_prs = 0
    if not url:
        if new_added:
            url = BASE_URL + \
                'repos/%s/%s/issues?per_page=100&state=all' % (owner, repoName)
        else:
            url = BASE_URL + \
                'repos/%s/%s/issues?per_page=100&state=all&since=%s&sort=updated' % (
                    owner, repoName, last_updated_at)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if response.status_code == 200:  # 200 = SUCCESS
        issues = response.json()
        _, u = saveIssues(repoName, issues, contributors, users)
        updated_prs = updated_prs + u
        if 'next' in response.links:
            _, u = getRepoIssues(owner, repoName, contributors, users,
                                 number, new_added, last_updated_at, response.links['next']['url'])
            updated_prs = updated_prs + u
    return contributors, updated_prs


def getRepoTotalIssueCount(repo):
    totalIssueCount = 0
    repoName = repo['name']
    owner = repo['owner']['login']
    url = BASE_URL + \
        'repos/%s/%s/issues?per_page=1&state=all&sort=updated_at' % (
            owner, repoName)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # 200 = SUCCESS
        issue = response.json()
        if len(issue) > 0:
            totalIssueCount = issue[0]['number']
    return totalIssueCount


def savePRs(repo, pullReq, contributors_, users, new_added):
    contributors = contributors_
    for pull in pullReq:
        username = pull['user']['login'].lower()
        if 'open' == pull['state']:
            created_at = datetime.strptime(
                pull['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if username not in users or repo not in users[username] or users[username][repo]['lastOpenPR'] < created_at:
                if username in contributors:
                    contributors[username]['open_prs'] += 1
                    if contributors[username]['last_open_pr'] is None or contributors[username]['last_open_pr'] < created_at:
                        contributors[username]['last_open_pr'] = created_at
                else:
                    contributors[username] = {}
                    contributors[username]['open_prs'] = 1
                    contributors[username]['issue_counts'] = 0
                    contributors[username]['merged_prs'] = 0
                    contributors[username]['closed_prs'] = 0
                    contributors[username]['last_open_pr'] = created_at
                    contributors[username]['last_merged_pr'] = None
                    contributors[username]['last_closed_pr'] = None
                    contributors[username]['last_issue'] = None
                    contributors[username]['avatar_url'] = pull['user']['avatar_url']
        elif 'closed' == pull['state'] and not pull['merged_at'] is None:
            merged_at = datetime.strptime(
                pull['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
            if username not in users or repo not in users[username] or users[username][repo]['lastMergedPR'] < merged_at:
                if username in contributors:
                    contributors[username]['merged_prs'] += 1
                    if contributors[username]['last_merged_pr'] is None or contributors[username]['last_merged_pr'] < merged_at:
                        contributors[username]['last_merged_pr'] = merged_at
                else:
                    contributors[username] = {}
                    contributors[username]['open_prs'] = 0
                    contributors[username]['issue_counts'] = 0
                    contributors[username]['merged_prs'] = 1
                    contributors[username]['closed_prs'] = 0
                    contributors[username]['last_open_pr'] = None
                    contributors[username]['last_closed_pr'] = None
                    contributors[username]['last_merged_pr'] = merged_at
                    contributors[username]['last_issue'] = None
                    contributors[username]['avatar_url'] = pull['user']['avatar_url']
        elif not new_added and 'closed' == pull['state'] and pull['merged_at'] is None:
            closed_at = datetime.strptime(
                pull['closed_at'], '%Y-%m-%dT%H:%M:%SZ')
            if username not in users or repo not in users[username] or users[username][repo]['lastClosedPR'] < closed_at:
                if username in contributors:
                    contributors[username]['closed_prs'] += 1
                else:
                    contributors[username] = {}
                    contributors[username]['open_prs'] = 0
                    contributors[username]['issue_counts'] = 0
                    contributors[username]['merged_prs'] = 0
                    contributors[username]['closed_prs'] = 1
                    contributors[username]['last_open_pr'] = None
                    contributors[username]['last_merged_pr'] = None
                    contributors[username]['last_closed_pr'] = closed_at
                    contributors[username]['last_issue'] = None
                    contributors[username]['avatar_url'] = pull['user']['avatar_url']

    return contributors


def saveIssues(repo, issues, contributors_, users):
    contributors = contributors_
    updated_prs = 0
    for issue in issues:
        if 'pull_request' not in issue:
            username = issue['user']['login'].lower()
            created_at = datetime.strptime(
                issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
            if username not in users or repo not in users[username] or users[username][repo]['lastIssue'] < created_at:
                if username in contributors:
                    contributors[username]['issue_counts'] += 1
                    if contributors[username]['last_issue'] is None or contributors[username]['last_issue'] < created_at:
                        contributors[username]['last_issue'] = created_at
                else:
                    contributors[username] = {}
                    contributors[username]['issue_counts'] = 1
                    contributors[username]['last_issue'] = created_at
                    contributors[username]['open_prs'] = 0
                    contributors[username]['last_open_pr'] = None
                    contributors[username]['last_merged_pr'] = None
                    contributors[username]['last_closed_pr'] = None
                    contributors[username]['merged_prs'] = 0
                    contributors[username]['closed_prs'] = 0
                    contributors[username]['avatar_url'] = issue['user']['avatar_url']
        else:
            updated_prs = updated_prs + 1
    return contributors, updated_prs


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
        'show_rank': SHOW_RANK,
        'total': len(data),
    }
    return render(request, 'core/gsoclist.html', context)


def sortUser(_User, key):
    if SORT == 1:
        all_list = _User.filter(user__gsoc=True).values(
            'user__login', 'user__id', 'user__avatar',
            'user__gsoc').annotate(Sum('totalIssues'),
                                   Sum('totalOpenPRs'),
                                   Sum('totalMergedPRs'),
                                   count=Sum('totalOpenPRs'))
    elif SORT == 2:
        all_list = _User.filter(user__gsoc=True).values(
            'user__login', 'user__id', 'user__avatar',
            'user__gsoc').annotate(Sum('totalIssues'),
                                   Sum('totalOpenPRs'),
                                   Sum('totalMergedPRs'),
                                   count=Sum('totalMergedPRs'))
    elif SORT == 3:
        all_list = _User.filter(user__gsoc=True).values(
            'user__login', 'user__id', 'user__avatar',
            'user__gsoc').annotate(Sum('totalIssues'),
                                   Sum('totalOpenPRs'),
                                   Sum('totalMergedPRs'),
                                   count=Sum('totalOpenPRs') + Sum('totalMergedPRs'))
    elif SORT == 4:
        all_list = _User.filter(user__gsoc=True).values(
            'user__login', 'user__id', 'user__avatar',
            'user__gsoc').annotate(Sum('totalIssues'),
                                   Sum('totalOpenPRs'),
                                   Sum('totalMergedPRs'),
                                   count=Sum('totalIssues'))
    elif SORT == 5:
        all_list = _User.filter(user__gsoc=True).values(
            'user__login', 'user__id', 'user__avatar',
            'user__gsoc').annotate(Sum('totalIssues'),
                                   Sum('totalOpenPRs'),
                                   Sum('totalMergedPRs'),
                                   count=Sum('totalOpenPRs') + Sum('totalIssues'))
    elif SORT == 6:
        all_list = _User.filter(user__gsoc=True).values(
            'user__login', 'user__id', 'user__avatar',
            'user__gsoc').annotate(Sum('totalIssues'),
                                   Sum('totalOpenPRs'),
                                   Sum('totalMergedPRs'),
                                   count=Sum('totalMergedPRs') + Sum('totalIssues'))
    elif SORT == 7:
        all_list = _User.filter(user__gsoc=True).values(
            'user__login', 'user__id', 'user__avatar',
            'user__gsoc').annotate(Sum('totalIssues'),
                                   Sum('totalOpenPRs'),
                                   Sum('totalMergedPRs'),
                                   count=Sum('totalIssues') + Sum('totalMergedPRs') + Sum('totalIssues'))
    all_list = all_list.order_by('-count', 'user__pk')
    rank = 1
    previous = None
    entries = list(all_list)
    if len(entries) > 0:
        previous = entries[0]
    else:
        previous = {}
    previous['rank'] = 1
    for i, entry in enumerate(entries[1:]):
        if entry['count'] != previous['count']:
            rank = i + 2
            entry['rank'] = str(rank)
        else:
            entry['rank'] = str(rank)
            previous['rank'] = entry['rank']
        previous = entry
    if key == 'i':
        entries.sort(key=lambda v: v['totalIssues__sum'], reverse=True)
    elif key == 'p':
        entries.sort(key=lambda v: v['totalOpenPRs__sum'], reverse=True)
    elif key == 'm':
        entries.sort(key=lambda v: v['totalMergedPRs__sum'], reverse=True)
    else:
        entries.sort(key=lambda v: v['count'], reverse=True)
    return entries
