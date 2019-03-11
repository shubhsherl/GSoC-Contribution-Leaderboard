import json
from django.shortcuts import render
from django.core import serializers
from django.conf import settings
import datetime
import time
import requests
from .models import User, LastUpdate

AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.API_BASE_URL
ORG = settings.ORGANIZATION


def github():
    success = False
    user = User.objects.filter(gsoc=True)
    gsoclist = json.loads(serializers.serialize(
        'json', list(user), fields=('login')))
    for user in gsoclist:
        username = user['fields']['login']
        success = getOpenPRs(username) and getMergedPRs(
            username) and getIssues(username)
    if success:
        if LastUpdate.objects.filter(pk=1):
            LastUpdate.objects.filter(pk=1).update(
                gList=datetime.datetime.now())
        else:
            updated = LastUpdate(pk=1, gList=datetime.datetime.now())
            updated.save()


def getMergedPRs(username):
    mergedPRs = -1
    url = BASE_URL + \
        'search/issues?q=org:%s+author:%s+archived:false+is:merged+is:pr' % (
            ORG, username)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # success
        mergedPRs = response.json()['total_count']
        user = User.objects.filter(login=username)
        if user:
            user.update(totalMergedPRs=mergedPRs)
    elif (response.status_code == 403):  # rate-limit exceeded wait for 30sec
        time.sleep(30)
        getMergedPRs(username)
    return mergedPRs != -1


def getIssues(username):
    issues = -1
    url = BASE_URL + \
        'search/issues?q=org:%s+author:%s+archived:false+is:issue' % (
            ORG, username)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):
        issues = response.json()['total_count']
        user = User.objects.filter(login=username)
        if user:
            user.update(totalIssues=issues)
    elif (response.status_code == 403):
        time.sleep(30)
        getIssues(username)
    return issues != -1


def getOpenPRs(username):
    openPRs = -1
    url = BASE_URL + \
        'search/issues?q=org:%s+author:%s+archived:false+is:open+is:pr' % (
            ORG, username)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):
        openPRs = response.json()['total_count']
        user = User.objects.filter(login=username)
        if user:
            user.update(totalOpenPRs=openPRs)
    elif (response.status_code == 403):
        time.sleep(30)
        getOpenPRs(username)
    return openPRs != -1
