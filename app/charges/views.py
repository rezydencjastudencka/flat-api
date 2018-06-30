import simplejson as json

from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound

from session.decorators import require_login
from .models import Charge


@require_POST
@require_login
def create(request):
    req = json.loads(request.body)

    if 'date' not in req or 'name' not in req or 'rawAmount' not in req or 'to' not in req:
        return HttpResponseBadRequest()

    date = datetime.strptime(req['date'], "%Y-%m-%dT%H:%M:%S.%fZ").date()

    with transaction.atomic():
        charge = Charge(from_user=request.user, raw_amount=req['rawAmount'], name=req['name'], date=date)
        charge.save()
        users = User.objects.filter(id__in=req['to'])
        charge.to_users.set(users)
        charge.clean()

    return HttpResponse(json.dumps(charge.to_json_as_revenue()), content_type='application/json')


@require_POST
@require_login
def delete(request):
    req = json.loads(request.body)

    if 'ids' not in req:
        return HttpResponseBadRequest()

    Charge.objects.filter(
        from_user=request.user,
        id__in=req['ids']
    ).delete()

    return HttpResponse(json.dumps({'error': 'ok'}), content_type='application/json')


@require_GET
@require_login
def get_expense(request, id):
    expense = Charge.objects.filter(
        to_users=request.user,
        id=id
    ).first()

    if expense is None:
        return HttpResponseNotFound()

    return HttpResponse(json.dumps(expense.to_json_as_expense()), content_type='application/json')


@require_GET
@require_login
def index(request, year, month):
    revenues = Charge.get_revenues(year, month, request.user)
    expenses = Charge.get_expenses(year, month, request.user)
    summary = Charge.get_summary(year, month, request.user, revenues=revenues, expenses=expenses)

    res = {
        'charges': [],  # TODO: change charges name
        'incomes': [],  # TODO: change incomes name
        'summary': list(summary.values()),
    }

    for revenue in revenues:
        res['charges'].append(revenue.to_json_as_revenue())

    for expense in expenses:
        res['incomes'].append(expense.to_json_as_expense())

    return HttpResponse(json.dumps(res), content_type='application/json')
