import random
import string
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin


def generate_join_token():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))


class Flat(ExportModelOperationsMixin('flat'), models.Model):
    name = models.CharField(max_length=255)
    join_token = models.CharField(max_length=32, default=generate_join_token)

    def __str__(self):
        return self.name

