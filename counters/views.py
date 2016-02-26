from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, HttpResponseBadRequest

from session.decorators import require_login

import json

# Create your views here.
from .models import Counter


@require_GET
@require_login
def index(request, counter_name):
    res = {'count': get_object_or_404(Counter, name=counter_name).counter}
    return HttpResponse(json.dumps(res))


@require_POST
@require_login
def modify(request, counter_name):
    req = json.loads(request.body)

    if 'amount' not in req or not isinstance(req['amount'], int):
        return HttpResponseBadRequest

    res = {'error': 'ok', 'count': Counter.modify_and_get(req['amount'], name=counter_name).counter}
    return HttpResponse(json.dumps(res))
