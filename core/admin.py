from django.contrib import admin
from .models import User, LastUpdate, Repository


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
    readonly_fields = ['login', 'avatar',
                       'totalCommits', 'totalPRs', 'totalIssues']
    list_filter = ['gsoc']
    search_fields = ['login']
    actions = [mark_gsoc, unmark_gsoc]


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