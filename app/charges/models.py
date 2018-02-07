from django.db import models
from django.contrib.auth.models import User
import numexpr as ne


class Charge(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    raw_amount = models.CharField(max_length=1023)
    date = models.DateField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="revenues")
    to_users = models.ManyToManyField(User, related_name="expenses")

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
    def get_expenses(year, month, user):
        return Charge.objects.filter(
            date__year=year,
            date__month=month,
            to_users=user
        )

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
