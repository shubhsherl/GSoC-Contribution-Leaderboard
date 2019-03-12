from django.contrib import admin
from .models import User, LastUpdate, Repository, Relation
from django.conf import settings
import requests



AUTH_TOKEN = settings.GITHUB_AUTH_TOKEN
BASE_URL = settings.API_BASE_URL


def mark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=True)


mark_gsoc.short_description = "Mark as GSoC Candidate"


def unmark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=False)


unmark_gsoc.short_description = "Unmark as GSoC Candidate"


def mark_repo_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=True)


mark_repo_gsoc.short_description = "Add as gsoc"


def remove_repo_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=False)


remove_repo_gsoc.short_description = "Remove Repository from gsoc"


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
        super().save_model(request, obj, form, change)
        base_repo, created = Repository.objects.get_or_create(repo='base_repo_1254879', defaults={'gsoc': True})
        Relation.objects.get_or_create(repo=base_repo, user=obj)


class LastUpdatedAdmin(admin.ModelAdmin):
    list_display = ['updated', 'pk']
    readonly_fields = ['updated']


class RepositoryAdmin(admin.ModelAdmin):
    list_display = ['repo', 'owner', 'gsoc','openIssues']
    readonly_fields = ['owner', 'repo']
    list_filter = ['gsoc']
    search_fields = ['owner', 'repo']
    actions = [mark_repo_gsoc, remove_repo_gsoc]


class RelationAdmin(admin.ModelAdmin):
    list_display = ['user', 'repo']
    readonly_fields = ['totalMergedPRs', 'totalOpenPRs', 'totalIssues']
    search_fields = ['user__login']


admin.site.register(User, UserAdmin)
admin.site.register(LastUpdate, LastUpdatedAdmin)
admin.site.register(Repository, RepositoryAdmin)
admin.site.register(Relation,RelationAdmin)
