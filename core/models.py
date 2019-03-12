from django.db import models


class User(models.Model):
    login = models.TextField(null=False, db_index=True)
    avatar = models.TextField(null=True)
    gsoc = models.BooleanField(default=False)

    def __str__(self):
        return self.login


class LastUpdate(models.Model):
    updated = models.DateTimeField(auto_now=True)


class Repository(models.Model):
    owner = models.TextField(null=False)
    repo = models.TextField(unique=True, null=False)
    gsoc = models.BooleanField(default=False)
    openIssues = models.IntegerField(default=-1)

    users = models.ManyToManyField(User, through='Relation', through_fields=('repo', 'user'), )

    def __str__(self):
        return self.repo


class Relation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    totalMergedPRs = models.IntegerField(default=0)
    totalOpenPRs = models.IntegerField(default=0)
    totalIssues = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'repo')
