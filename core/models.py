from django.db import models
from django.contrib.postgres.fields import ArrayField


class User(models.Model):
    login = models.TextField(null=False)
    avatar = models.TextField(null=True)

    # TODO: Add user details for individual repos
    # repos = ArrayField(models.TextField(),size= 10, null=True, blank=True,)
    # reposCommits = ArrayField(models.IntegerField(default=0),size= 10, null=True, blank=True)
    # reposAdd = ArrayField(models.IntegerField(default=0),size= 10, null=True, blank=True)
    # reposDelete = ArrayField(models.IntegerField(default=0),size= 10, null=True, blank=True)
    gsoc = models.BooleanField(default=False)

    def __str__(self):
        return self.login


class LastUpdate(models.Model):
    updated = models.DateTimeField(auto_now=True)

class Repository(models.Model):
    owner = models.TextField(null=False)
    repo = models.TextField(unique=True, null=False)
    include = models.BooleanField(default=False)
    openIssues= models.IntegerField(default=-1)

    users=models.ManyToManyField(User,through='Relation',through_fields=('repo', 'user'),)

    def __str__(self):
        return self.repo

class Relation(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    repo=models.ForeignKey(Repository, on_delete=models.CASCADE)
    totalCommits = models.IntegerField(default=0)
    totalPRs = models.IntegerField(default=0)
    totalIssues = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'repo')