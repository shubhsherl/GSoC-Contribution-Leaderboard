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
    users = User.objects.filter(gsoc=True)
    for user in users:
        user.totalOpenPRs=getOpenPRs(user.login)
        user.totalMergedPRs=getMergedPRs(user.login)
        user.totalIssues=getIssues(user.login)
        user.save()
    updated = LastUpdate.objects.filter(pk=1)
    if updated:
        updated.update(update=datetime.datetime.now())
    else:
        updated = LastUpdate(pk=1, update=datetime.datetime.now())
        updated.save()


def getMergedPRs(username):
    mergedPRs = -1
    url = BASE_URL + \
        'search/issues?q=org:%s+author:%s+archived:false+is:merged+is:pr' % (
            ORG, username)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):  # success
        return response.json()['total_count']
    elif (response.status_code == 403):  # rate-limit exceeded wait for 30sec
        time.sleep(30)
        return getMergedPRs(username)
    return mergedPRs


def getIssues(username):
    issues = -1
    url = BASE_URL + \
        'search/issues?q=org:%s+author:%s+archived:false+is:issue' % (
            ORG, username)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):
        return response.json()['total_count']
    elif (response.status_code == 403):
        time.sleep(30)
        return getIssues(username)
    return issues


def getOpenPRs(username):
    openPRs = -1
    url = BASE_URL + \
        'search/issues?q=org:%s+author:%s+archived:false+is:open+is:pr' % (
            ORG, username)
    response = requests.get(
        url, headers={"Authorization": "token " + AUTH_TOKEN})
    if (response.status_code == 200):
        return response.json()['total_count']
    elif (response.status_code == 403):
        time.sleep(30)
        return getOpenPRs(username)
    return openPRs
