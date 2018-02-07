import simplejson as json
from django.http import HttpResponseBadRequest, HttpResponse

from django.views.decorators.http import require_POST
from fcm_django.models import FCMDevice

from session.decorators import require_login


@require_login
@require_POST
def device(request):
    req = json.loads(request.body.decode("utf-8"))

    if 'registration_token' not in req:
        return HttpResponseBadRequest()

    FCMDevice(registration_id=req['registration_token'],
              type='android', user=request.user).save()

    return HttpResponse(status=204)
