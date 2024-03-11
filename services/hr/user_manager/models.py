from django.db import models


class User(models.Model):
    user_id = models.AutoField(primary_key=True, )
    email = models.CharField(max_length=200, unique=True, null=False, blank=False)
    username = models.CharField(max_length=50, unique=True, null=False, blank=False)
    roles = models.CharField(max_length=1200, null=False)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
