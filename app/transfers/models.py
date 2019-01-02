from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django_prometheus.models import ExportModelOperationsMixin
from charges.models import Charge


class Transfer(ExportModelOperationsMixin('transfer'), models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="outgoing_transfers")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incoming_transfers")

    def __str__(self):
        return '{}: {}'.format(self.from_user.username, self.name)

    @staticmethod
    def get_user_transfers(year, month, user):
        return Transfer.objects.filter(
            Q(to_user=user) | Q(from_user=user),
            date__year=year,
            date__month=month
        )
