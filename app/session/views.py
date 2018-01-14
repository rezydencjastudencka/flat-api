import json

from django.http import HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login, logout


@require_POST
def create(request):
    req = json.loads(request.body.decode("utf-8"))

    if 'name' not in req or 'password' not in req:
        return HttpResponseBadRequest()

    user = authenticate(username=req['name'], password=req['password']);

    if user is None:
        return HttpResponseNotFound()

    if not user.is_active:
        return HttpResponseForbidden()

    login(request, user)

    return HttpResponse(json.dumps({'error': 'ok'}), content_type='application/json')


@require_GET
def check(request):
    if request.user.is_authenticated():
        return HttpResponse(json.dumps({'error': 'ok'}), content_type='application/json')
    else:
        return HttpResponseNotFound()


@require_POST
def remove(request):
    logout(request)
    return HttpResponse(json.dumps({'error': 'ok'}), content_type='application/json')
