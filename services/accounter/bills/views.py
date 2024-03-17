import datetime
import json
from collections import defaultdict

from django.db import transaction
from django.http import HttpResponse, HttpRequest
from django.utils import timezone

from .roles import allowed_roles
from . import models
from . import queue


@allowed_roles('popug_admin')
def close_period(request: HttpRequest) -> HttpResponse:
    # ручка для закрытия периода
    if request.method == 'POST':
        with transaction.atomic():
            period = models.BillingPeriod.objects.create(
                end_time=timezone.now(),
            )
            # publish EndBillingPeriod event
            queue.get_client().publish_message(
                routing_key='EndBillingPeriod',
                message={
                    'name': 'EndBillingPeriod',
                    'params': {
                        'period_id': period.period_id,
                        'end_time': period.end_time,
                    }
                }
            )
        return HttpResponse(f'Period N {period.period_id} closed')
    else:
        raise NotImplementedError(f'not supported method {request.method}')


def bills_my(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        # Инфа - сколько денег заработано попугом (лог операций + текущий баланс)
        username = request.headers['X-Forwarded-User']
        account = models.Account.objects.get(user__username=username)
        balance = account.balance
        operations_log = models.Transaction.objects.filter(
            account=account,
            created_at__lte=account.updated_at,  # чтобы избежать несоответствия при параллельном изменении баланса
        ).order_by(
            '-created_at',
        ).values(
            'amount', 'description', 'created_at', 'direction',
        )

        resp = {
            'balance': balance,
            'operations': list(operations_log),
        }
        return HttpResponse(json.dumps(resp))
    else:
        raise NotImplementedError(f'not supported method {request.method}')


@allowed_roles('popug_admin', 'popug_accounter')
def bills(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        # Инфа - сколько денег заработано менеджерами (за текущий период)
        last_period = models.BillingPeriod.objects.order_by('-end_time').first()
        transactions_qs = models.Transaction.objects.all().values('amount', 'direction')

        if last_period is not None:
            transactions_qs = transactions_qs.filter(
                created_at__gte=last_period.end_time,
            )

        surplus = 0.0
        expenses = 0.0
        for tr in transactions_qs:
            if tr['direction'] == 1:
                expenses += tr['amount']
            else:
                surplus += tr['amount']
        resp = {
            'surplus': surplus,
            'expenses': expenses,
            'result': surplus - expenses,
        }
        return HttpResponse(json.dumps(resp))
    else:
        raise NotImplementedError(f'not supported method {request.method}')


@allowed_roles('popug_admin')
def analytics(request: HttpRequest) -> HttpResponse:
    # show managers income in current period, how many users in negative balance in current period, and most expensive task in current period
    if request.method == 'GET':
        from_time = datetime.date(1970, 1, 1)
        end_time = timezone.now()
        if last_period := models.BillingPeriod.objects.order_by('-end_time').first():
            from_time = last_period.end_time

        transactions_qs = models.Transaction.objects.filter(
            created_at__gt=from_time,
            created_at__lte=end_time,
        ).values(
            'account_id',
            'amount',
            'direction',
            'description',
        )

        surplus = 0.0
        expenses = 0.0
        account_balances = defaultdict(float)

        for tr in transactions_qs:
            if tr['direction'] == 1:
                expenses += tr['amount']
                account_balances['account_id'] += tr['amount']
            else:
                surplus += tr['amount']
                account_balances['account_id'] -= tr['amount']

        num_users_in_negative = sum(balance < 0 for balance in account_balances.values())
        most_expensive_task = models.Transaction.objects.filter(
            created_at__gt=from_time,
            created_at__lte=end_time,
            direction=1,
        ).order_by('-amount').first()

        resp = {
            'Management result': surplus - expenses,
            'Num users in negative': num_users_in_negative,
            'Most expensive task': {
                'user_id': most_expensive_task.account.user.user_id,
                'description': most_expensive_task.description,
                'amount': most_expensive_task.amount,
            }
        }
        return HttpResponse(json.dumps(resp))
    else:
        raise NotImplementedError(f'not supported method {request.method}')
