from django.contrib import admin
from .models import User, LastUpdate, Repository
from django.conf import settings
import requests
import json


AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.BASE_URL


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
                       'totalCommits', 'totalPRs', 'totalIssues']
    list_filter = ['gsoc']
    search_fields = ['login']
    actions = [mark_gsoc, unmark_gsoc]

    def save_model(self, request, obj, form, change):
        url = BASE_URL + 'users/%s' % obj.login
        response = requests.get(
            url, headers={"Authorization": "token " + AUTH_TOKEN})
        if (response.status_code == 200):
            print(response.json())
            obj.avatar = response.json()['avatar_url']
        super().save_model(request, obj, form, change)


class LastUpdatedAdmin(admin.ModelAdmin):
    list_display = ['updated']
    readonly_fields = ['updated']


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['owner', 'repo', 'include']
    readonly_fields = ['owner', 'repo']
    list_filter = ['include']
    search_fields = ['owner', 'repo']
    actions = [include_repo, remove_repo]


admin.site.register(User, UserAdmin)
admin.site.register(LastUpdate, LastUpdatedAdmin)
admin.site.register(Repository, RepositoryAdmin)
