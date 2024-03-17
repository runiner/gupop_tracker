from django.db import models


class User(models.Model):
    user_id = models.IntegerField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, null=False, blank=False)
    roles = models.CharField(max_length=1200, null=False)


class Account(models.Model):
    account_id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    transaction_id = models.IntegerField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(null=True, blank=True)
    direction = models.IntegerField(null=False, blank=False, choices=[(1, 'IN'), (-1, 'OUT')])


class BillingPeriod(models.Model):
    period_id = models.IntegerField(primary_key=True)
    end_time = models.DateTimeField(null=False, blank=False)


class Task(models.Model):
    task_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=250, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    assign_cost = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    complete_cost = models.DecimalField(max_digits=10, decimal_places=2, null=False)
