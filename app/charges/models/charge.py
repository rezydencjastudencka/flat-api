from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
import numexpr as ne
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from fcm_django.models import FCMDevice
from django_prometheus.models import ExportModelOperationsMixin


class Charge(ExportModelOperationsMixin('charge'), models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    raw_amount = models.CharField(max_length=1023)
    date = models.DateField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="revenues")
    to_users = models.ManyToManyField(User, related_name="expenses")

    def __str__(self):
        return '{}: {}'.format(self.from_user.username, self.name)

    def clean(self):
        flat = self.from_user.profile.flat
        if any(user.profile.flat != flat for user in self.to_users.all()):
            raise ValidationError('You cannot charge user from different flat.')

    def save(self, *args, **kwargs):
        self.amount = float(ne.evaluate(self.raw_amount, local_dict={}, global_dict={}, truediv=True))
        super(Charge, self).save(*args, **kwargs)

    def to_json_as_revenue(self):
        to_users = []
        for user in self.to_users.all():
            to_users.append({
                'id': user.id,
                'name': user.username,
                'room': 1  # TODO
            })

        return {
            'amount': self.amount,
            'date': self.date.isoformat(),
            'from': self.from_user_id,
            'id': self.id,
            'name': self.name,
            'rawAmount': self.raw_amount,
            'to': to_users
        }

    def to_json_as_expense(self):
        to_users = []
        for user in self.to_users.all():
            to_users.append({
                'id': user.id,
                'name': user.username,
                'room': 1  # TODO
            })

        return {
            'amount': self.amount / len(to_users),
            'date': self.date.isoformat(),
            'from': {
                'id': self.from_user.id,
                'name': self.from_user.username,
                'room': 1  # TODO
            },
            'id': self.id,
            'name': self.name,
            'rawAmount': self.raw_amount,
            'to': to_users
        }

    @staticmethod
    def get_revenues(year, month, user):
        return Charge.objects.filter(
            date__year=year,
            date__month=month,
            from_user=user
        )

    @staticmethod
    def get_revenue(id, user):
        return Charge.objects.filter(
            id=id,
            from_user=user
        ).first()

    @staticmethod
    def get_expenses(year, month, user):
        return Charge.objects.filter(
            date__year=year,
            date__month=month,
            to_users=user
        )

    @staticmethod
    def get_expense(id, user):
        return Charge.objects.filter(
            id=id,
            to_users=user
        ).first()

    @staticmethod
    def get_summary(year, month, user, revenues=None, expenses=None):
        if revenues is None:
            revenues = Charge.get_revenues(year, month, user)

        if expenses is None:
            expenses = Charge.get_expenses(year, month, user)

        summary = {}

        for user in User.objects.all():
            summary[user.id] = {
                'amount': 0,
                'id': user.id,
                'name': user.username,
                'room': 1  # TODO
            }

        for revenue in revenues:
            users = revenue.to_users.all()
            for user in users:
                summary[user.id]['amount'] -= revenue.amount / len(users)

        for expense in expenses:
            summary[expense.from_user_id]['amount'] += expense.amount / expense.to_users.count()

        return summary

    @staticmethod
    def get_summary_new(year, month, user):
        revenues = Charge.get_revenues(year, month, user)
        expenses = Charge.get_expenses(year, month, user)

        summary = {}

        def get_or_add(user_to_get):
            if user_to_get.id not in summary.keys():
                summary[user_to_get.id] = {'user': user_to_get, 'amount': 0}
            return summary[user_to_get.id]

        for revenue in revenues:
            rev_users = revenue.to_users.all()
            for rev_user in rev_users:
                entry = get_or_add(rev_user)
                entry['amount'] -= revenue.amount / len(rev_users)

        for expense in expenses:
            entry = get_or_add(expense.from_user)
            entry['amount'] += expense.amount / expense.to_users.count()

        for user in User.objects.filter(profile__flat=user.profile.flat):
            get_or_add(user)

        return summary


@receiver(m2m_changed, sender=Charge.to_users.through)
def _send_fcm_message(**kwargs):
    if not kwargs['action'] == 'post_add':
        return
    charge = kwargs['instance']
    for user_id in kwargs['pk_set']:
        if user_id != charge.from_user_id:
            FCMDevice.objects.filter(user_id=user_id).send_message(
                data={'type': 'new_expense', 'expense_id': str(charge.id)})
