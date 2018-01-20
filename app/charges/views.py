import simplejson as json

from datetime import datetime

from django.contrib.auth.models import User
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.http import HttpResponse, HttpResponseBadRequest

from session.decorators import require_login
from .models import Charge


@require_POST
@require_login
def create(request):
    req = json.loads(request.body)

    if 'date' not in req or 'name' not in req or 'rawAmount' not in req or 'to' not in req:
        return HttpResponseBadRequest()

    date = datetime.strptime(req['date'], "%Y-%m-%dT%H:%M:%S.%fZ").date()

    charge = Charge(from_user=request.user, raw_amount=req['rawAmount'], name=req['name'], date=date)
    charge.save()
    charge.to_users = User.objects.filter(id__in=req['to'])

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
        to_users = []
        for user in expense.to_users.all():
            to_users.append({
                'id': user.id,
                'name': user.username,
                'room': 1  # TODO
            })

        res['incomes'].append({
            'amount': expense.amount / len(to_users),
            'date': expense.date.isoformat(),
            'from': {
                'id': expense.from_user.id,
                'name': expense.from_user.username,
                'room': 1  # TODO
            },
            'id': expense.id,
            'name': expense.name,
            'rawAmount': expense.raw_amount,
            'to': to_users
        })

    return HttpResponse(json.dumps(res), content_type='application/json')
