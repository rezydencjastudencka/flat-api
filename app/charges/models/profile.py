from django.contrib.auth.models import User
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin

from charges.models.flat import Flat


class Profile(ExportModelOperationsMixin('profile'), models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    flat = models.ForeignKey(Flat, on_delete=models.PROTECT)
