from django.db import models
from datetime import datetime


class User(models.Model):
    login = models.TextField(unique=True, null=False, db_index=True)
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
    updatedAt = models.DateTimeField(auto_now=datetime(2000,1,1,1,30,30))
    totalIssues = models.IntegerField(default=-1)

    users = models.ManyToManyField(
        User, through='Relation', through_fields=('repo', 'user'), )

    def __str__(self):
        return self.repo


class RelationManager(models.Manager):
    def get_dict(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT r.id, u.login, re.repo, r.lastMergedPR, r.lastOpenPR, r.lastIssue, r.lastClosedPR
                FROM core_relation r, core_user u, core_repository re
                WHERE r.user_id = u.id AND r.repo_id = re.id
                """)
            all_user = {}
            for row in cursor.fetchall():
                last = {
                    'lastMergedPR': row[3],
                    'lastOpenPR': row[4],
                    'lastIssue': row[5],
                    'lastClosedPR': row[6],
                }
                user = row[1]
                repo = row[2]
                if not user in all_user:
                    all_user[user] = {}
                all_user[user][repo] = last
        return all_user


class Relation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repo = models.ForeignKey(Repository, on_delete=models.CASCADE)
    totalMergedPRs = models.IntegerField(default=0)
    totalOpenPRs = models.IntegerField(default=0)
    totalIssues = models.IntegerField(default=0)
    #for merged PR merged_at
    lastMergedPR = models.DateTimeField(default=datetime(2000,1,1,1,30,30))
    #for open PR created_at
    lastOpenPR = models.DateTimeField(auto_now=datetime(2000,1,1,1,30,30))
    #for closed PR closed_at
    lastClosedPR = models.DateTimeField(auto_now=datetime(2000,1,1,1,30,30))
    lastIssue = models.DateTimeField(auto_now=datetime(2000,1,1,1,30,30))
    objects = RelationManager()

    class Meta:
        unique_together = ('user', 'repo')
