from django.http import HttpResponse, HttpRequest

from .roles import allowed_roles


@allowed_roles('popug_admin')
def close_period(request: HttpRequest) -> HttpResponse:
    # ручка для закрытия периода (период два таймстампа "от" и "до", лог операций - содержит таймстамп)
    if request.method == 'POST':
        return HttpResponse('Period closed')
    else:
        raise NotImplementedError(f'not supported method {request.method}')


def bills_my(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        # TODO: get bills for current user
        # Инфа - сколько денег заработано попугом (лог операций + текущий баланс)
        return HttpResponse('Popug earned some money')
    else:
        raise NotImplementedError(f'not supported method {request.method}')


@allowed_roles('popug_admin', 'popug_accounter')
def bills(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        # Инфа - сколько денег заработано менеджерами (за текущий период)
        return HttpResponse('Statistics on popug earned money in current period')
    else:
        raise NotImplementedError(f'not supported method {request.method}')
