from django.contrib import admin, messages
from .models import User, LastUpdate, Repository, Relation
from django.conf import settings
import requests


AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.API_BASE_URL
ORG = settings.ORGANIZATION


def mark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=True)


mark_gsoc.short_description = "Mark as GSoC Candidate"


def unmark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=False)


unmark_gsoc.short_description = "Unmark as GSoC Candidate"


def mark_repo_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=True)


mark_repo_gsoc.short_description = "Mark as GSoC Repository"


def remove_repo_gsoc(modeladmin, request, queryset):
    queryset.update(openIssues=-1, totalIssues=-1, gsoc=False)


remove_repo_gsoc.short_description = "Unmark as GSoC Repository"


class UserAdmin(admin.ModelAdmin):
    list_display = ['login', 'gsoc']
    readonly_fields = ['avatar']
    list_filter = ['gsoc']
    search_fields = ['login']
    actions = [mark_gsoc, unmark_gsoc]

    def save_model(self, request, obj, form, change):
        obj.login = obj.login.lower()
        url = BASE_URL + 'users/%s' % obj.login
        response = requests.get(
            url, headers={"Authorization": "token " + AUTH_TOKEN})
        if response.status_code == 200:
            obj.avatar = response.json()['avatar_url']
        elif response.status_code == 404:
            messages.error(request, 'Invalid User')
            return False
        super().save_model(request, obj, form, change)
        base_repo, created = Repository.objects.get_or_create(
            repo=ORG, defaults={'gsoc': True})
        Relation.objects.get_or_create(repo=base_repo, user=obj)


class LastUpdatedAdmin(admin.ModelAdmin):
    list_display = ['updated', 'pk']
    readonly_fields = ['updated']


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['repo', 'owner', 'gsoc']
    readonly_fields = ['owner', 'repo', 'updatedAt']
    list_filter = ['gsoc']
    search_fields = ['owner', 'repo']
    actions = [mark_repo_gsoc, remove_repo_gsoc]


class RelationAdmin(admin.ModelAdmin):
    list_display = ['user', 'repo']
    readonly_fields = ['totalMergedPRs', 'totalOpenPRs',
                       'totalIssues', 'lastMergedPR', 'lastOpenPR', 'lastIssue']
    search_fields = ['user__login']


admin.site.register(User, UserAdmin)
admin.site.register(LastUpdate, LastUpdatedAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(Relation, RelationAdmin)
