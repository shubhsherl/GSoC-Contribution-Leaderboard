from django.db import models
from django.contrib.postgres.fields import ArrayField


class User(models.Model):
    login = models.TextField(unique=True, null=False)
    avatar = models.TextField(null=True)
    totalCommits = models.IntegerField(default=0)
    totalPRs = models.IntegerField(default=0)
    totalIssues = models.IntegerField(default=0)
    # TODO: Add user details for individual repos
    # repos = ArrayField(models.TextField(),size= 10, null=True, blank=True,)
    # reposCommits = ArrayField(models.IntegerField(default=0),size= 10, null=True, blank=True)
    # reposAdd = ArrayField(models.IntegerField(default=0),size= 10, null=True, blank=True)
    # reposDelete = ArrayField(models.IntegerField(default=0),size= 10, null=True, blank=True)
    gsoc = models.BooleanField(default=False)


class LastUpdate(models.Model):
    updated = models.DateTimeField(auto_now=True)

class Repository(models.Model):
    owner = models.TextField(null=False)
    repo = models.TextField(unique=True, null=False)
    include = models.BooleanField(default=False)


