from django.shortcuts import render
from django.conf import settings
import requests
import operator
from github import Github, GithubException

def github(request):
    search_result = {}
    contributors = []
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
    return render(request, 'core/github.html', {'search_result': search_result,'search_was_successful': True, 'contributors': contributors})

def getOrganizationContributors(repoList):
    contributors = {}
    for repo in repoList:
        # contributors.extend(getRepoContributors(repo))
        userList = getRepoContributors(repo)
        for user in userList:
            if user['login'] in contributors:
                contributors[user['login']]['commits'] += user['contributions']
            else:
                contributors[user['login']] = {}
                contributors[user['login']]['commits'] = user['contributions']
                contributors[user['login']]['avatar'] = user['avatar_url']
    return contributors

def getRepoContributors(repo):
    url = 'https://api.github.com/repos/%s/%s/contributors' %(repo['owner']['login'], repo['name'])
        response = requests.get(url, headers={"Authorization":"token GITHUB_TOKEN"}) 
    return response.json()
