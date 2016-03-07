import simplejson as json

from django.contrib.auth.models import User

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from session.decorators import require_login


@require_GET
@require_login
def index(request):
    users = User.objects.all()

    res = []

    for user in users:
        res.append({
            'id': user.id,
            'name': user.username
        })

    return HttpResponse(json.dumps(res))


@require_GET
@require_login
def show(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    res = {
        'id': user.id,
        'name': user.username
    }

    return HttpResponse(json.dumps(res))
