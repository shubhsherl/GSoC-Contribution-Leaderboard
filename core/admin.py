from django.contrib import admin
from .models import User, LastUpdate


def mark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=True)


mark_gsoc.short_description = "Mark as GSoC Candidate"


def unmark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=False)


unmark_gsoc.short_description = "Unmark as GSoC Candidate"


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


admin.site.register(User, UserAdmin)
admin.site.register(LastUpdate, LastUpdatedAdmin)
