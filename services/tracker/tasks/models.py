from django.db import models


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, null=False, blank=False)
    roles = models.CharField(max_length=1200, null=False)
