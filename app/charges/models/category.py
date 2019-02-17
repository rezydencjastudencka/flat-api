from django.db import models

from django_prometheus.models import ExportModelOperationsMixin


class Category(ExportModelOperationsMixin('category'), models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
