from django.db import models


class User(models.Model):
    login = models.TextField(unique=True, null=False)
    avatar = models.TextField(null=True)
    totalMergedPRs = models.IntegerField(default=0)
    totalOpenPRs = models.IntegerField(default=0)
    totalIssues = models.IntegerField(default=0)
    gsoc = models.BooleanField(default=False)

class LastUpdate(models.Model):
    update = models.DateTimeField(auto_now=True)