from fcm_django.models import FCMDevice


class Notification:
    def __init__(self, recipient_ids):
        self.recipient_ids = recipient_ids

    def recipient_devices(self):
        return FCMDevice.objects.filter(user_id__in=self.recipient_ids)

    def message(self):
        pass

    def send(self):
        self.recipient_devices().send_message(data=self.message())


class SkipCreatorNotification(Notification):
    @staticmethod
    def discard_creator(creator_id, affected_user_ids):
        recipient_ids = set(affected_user_ids)
        recipient_ids.discard(creator_id)
        return recipient_ids

    def __init__(self, entity, affected_user_ids):
        super().__init__(self.discard_creator(entity.from_user_id, affected_user_ids))


class ExpenseNotification(SkipCreatorNotification):
    def __init__(self, expense, recipient_ids):
        super().__init__(expense, recipient_ids)
        self.expense_id = expense.id

    def message(self):
        return {'type': 'new_expense', 'expense_id': str(self.expense_id)}
