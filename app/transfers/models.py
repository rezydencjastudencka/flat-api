from django.contrib.auth.models import User
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin
from charges.models import Charge


class Transfer(ExportModelOperationsMixin('transfer'), models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="outgoing_transfers")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="incoming_transfers")

    @staticmethod
    def get_incoming(year, month, user):
        return Transfer.objects.filter(
            date__year=year,
            date__month=month,
            to_user=user
        )

    @staticmethod
    def get_outgoing(year, month, user):
        return Transfer.objects.filter(
            date__year=year,
            date__month=month,
            from_user=user
        )

    @staticmethod
    def get_summary(year, month, user, incoming=None, outgoing=None, charges_summary=None):
        if incoming is None:
            incoming = Transfer.get_incoming(year, month, user)

        if outgoing is None:
            outgoing = Transfer.get_outgoing(year, month, user)

        if charges_summary is None:
            charges_summary = Charge.get_summary(year, month, user)

        summary = charges_summary

        for income in incoming:
            summary[income.from_user_id]['amount'] += income.amount

        for outcome in outgoing:
            summary[outcome.to_user_id]['amount'] -= outcome.amount

        return summary
