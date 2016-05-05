from datetime import datetime
import simplejson as json

from django.contrib.auth.models import User

from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET, require_POST

from session.decorators import require_login
from transfers.models import Transfer


@require_login
@require_GET
def index(request, year, month):
    incoming = Transfer.get_incoming(year, month, request.user)
    outgoing = Transfer.get_outgoing(year, month, request.user)
    summary = Transfer.get_summary(year, month, request.user, incoming=incoming, outgoing=outgoing)

    res = {
        'incoming': [],
        'outgoing': [],
        'summary': list(summary.values())
    }

    for income in incoming:
        res['incoming'].append({
            'id': income.id,
            'name': income.name,
            'amount': income.amount,
            'date': income.date.isoformat(),
            'from': {
                'id': income.from_user.id,
                'name': income.from_user.username,
                'room': 1,  # TODO
            },
            'to': {
                'id': income.to_user.id,
                'name': income.to_user.username,
                'room': 1,  # TODO
            }
        })

    for outcome in outgoing:
        res['outgoing'].append({
            'id': outcome.id,
            'name': outcome.name,
            'amount': outcome.amount,
            'date': outcome.date.isoformat(),
            'from': {
                'id': outcome.from_user.id,
                'name': outcome.from_user.username,
                'room': 1,  # TODO
            },
            'to': {
                'id': outcome.to_user.id,
                'name': outcome.to_user.username,
                'room': 1,  # TODO
            }
        })

    return HttpResponse(json.dumps(res), content_type="application/json")


def create(request):
    req = json.loads(request.body.decode("utf-8"))

    if 'date' not in req or 'name' not in req or 'amount' not in req or 'to' not in req:
        return HttpResponseBadRequest()

    date = datetime.strptime(req['date'], "%Y-%m-%dT%H:%M:%S.%fZ")

    transfer = Transfer(from_user=request.user, to_user=User.objects.get(pk=req['to']), amount=req['amount'],
                        name=req['name'], date=date)
    transfer.save()

    return HttpResponse()


@require_POST
@require_login
def delete(request):
    req = json.loads(request.body.decode("utf-8"))

    if 'ids' not in req:
        return HttpResponseBadRequest()

    Transfer.objects.filter(
        from_user=request.user,
        id__in=req['ids']
    ).delete()

    return HttpResponse()
