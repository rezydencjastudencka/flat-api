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


class ExpenseNotification(Notification):
    def __init__(self, expense, recipient_ids):
        super().__init__(recipient_ids)
        self.expense_id = expense.id

    def message(self):
        return {'type': 'new_expense', 'expense_id': str(self.expense_id)}
