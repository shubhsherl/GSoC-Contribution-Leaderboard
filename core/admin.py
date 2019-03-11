from django.contrib import admin,messages
from .models import User, LastUpdate
from django.conf import settings
import requests
import json

ORG = settings.ORGANIZATION
AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.API_BASE_URL


def mark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=True)


mark_gsoc.short_description = "Mark as GSoC Candidate"


def unmark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=False)


unmark_gsoc.short_description = "Unmark as GSoC Candidate"


def include_repo(modeladmin, request, queryset):
    queryset.update(include=True)


include_repo.short_description = "Include Repository"


def remove_repo(modeladmin, request, queryset):
    queryset.update(include=False)


remove_repo.short_description = "Remove Repository"


class UserAdmin(admin.ModelAdmin):
    list_display = ['login', 'gsoc']
    readonly_fields = ['avatar',
                        'totalOpenPRs', 'totalMergedPRs', 'totalIssues']
    list_filter = ['gsoc']
    search_fields = ['login']
    actions = [mark_gsoc, unmark_gsoc]

    def save_model(self, request, obj, form, change):
        obj.login = obj.login.lower()
        # Avatar
        url = BASE_URL + 'users/%s' % obj.login
        response = requests.get(
            url, headers={"Authorization": "token " + AUTH_TOKEN})
        if (response.status_code == 200):
            obj.avatar = response.json()['avatar_url']
        elif (response.status_code == 404):
            messages.error(request, 'Invalid User')
            return False
        # Merged PRs
        url = url = BASE_URL + 'search/issues?q=org:%s+author:%s+archived:false+is:merged+is:pr' % (ORG, obj.login)
        response = requests.get(
            url, headers={"Authorization": "token " + AUTH_TOKEN})
        if (response.status_code == 200):
            obj.totalMergedPRs = response.json()['total_count']  
        # Issues           
        url = BASE_URL + 'search/issues?q=org:%s+author:%s+archived:false+is:issue' % (ORG, obj.login)
        response = requests.get(
            url, headers={"Authorization": "token " + AUTH_TOKEN})
        if (response.status_code == 200):
            obj.totalIssues = response.json()['total_count']
        # Open PRs
        url = BASE_URL + 'search/issues?q=org:%s+author:%s+archived:false+is:open+is:pr' % (ORG, obj.login)         
        response = requests.get(
            url, headers={"Authorization": "token " + AUTH_TOKEN})
        if (response.status_code == 200):
            obj.totalOpenPRs = response.json()['total_count']
        super().save_model(request, obj, form, change)


class LastUpdatedAdmin(admin.ModelAdmin):
    list_display = ['gList', 'allList']
    readonly_fields = ['gList', 'allList']


admin.site.register(User, UserAdmin)
admin.site.register(LastUpdate, LastUpdatedAdmin)
