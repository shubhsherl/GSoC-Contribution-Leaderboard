from django.contrib import admin
from .models import User

def mark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=True)
mark_gsoc.short_description = "Mark Selected as GSoC Aspirants"

def unmark_gsoc(modeladmin, request, queryset):
    queryset.update(gsoc=False)
unmark_gsoc.short_description = "Unmark Selected as GSoC Aspirants"

class UserAdmin(admin.ModelAdmin):
    list_display = ['login', 'gsoc']
    list_filter = ['gsoc']
    search_fields = ['login']
    actions = [mark_gsoc, unmark_gsoc]

admin.site.register(User, UserAdmin)
