from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class User(models.Model):
    login = models.TextField(unique=True, null=False)
    avatar = models.TextField(null=True)
    totalCommits = models.IntegerField(default=0)
    totalAdd = models.IntegerField(default=0)
    totalDelete = models.IntegerField(default=0)
    repos = ArrayField(models.TextField(),size= 10, null=True)
    reposCommits = ArrayField(models.IntegerField(default=0),size= 10, null=True)
    reposAdd = ArrayField(models.IntegerField(default=0),size= 10, null=True)
    reposDelete = ArrayField(models.IntegerField(default=0),size= 10, null=True)
    gsoc = models.BooleanField(default=False)

class Glist(models.Model):
    login = models.TextField(unique=True, null=False)