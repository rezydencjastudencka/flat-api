from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from fcm_django.models import FCMDevice
from charges.models import Charge


class ExpenseNotification:
    def __init__(self, charge, affected_user_ids):
        self.charge_id = charge.id
        self.recipient_ids = self.get_recipients(charge, affected_user_ids)

    def get_recipients(self, charge, affected_user_ids):
        affected_user_ids.discard(charge.from_user_id)
        return affected_user_ids

    def get_message(self):
        return {'type': 'new_expense', 'expense_id': str(self.charge_id)}

    def send(self):
        FCMDevice.objects.filter(user_id__in=self.recipient_ids).send_message(data=self.get_message())


@receiver(m2m_changed, sender=Charge.to_users.through)
def _send_fcm_message(**kwargs):
    if not kwargs['action'] == 'post_add':
        return

    charge = kwargs['instance']
    affected_user_ids = kwargs['pk_set']

    ExpenseNotification(charge, affected_user_ids).send()
