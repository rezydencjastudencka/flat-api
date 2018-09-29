from django.apps import AppConfig
from django.db.models.signals import m2m_changed


def connect_notification(notification_class, model):
    from fcm.signals import notification_callback
    m2m_changed.connect(notification_callback(notification_class), weak=False, sender=model.to_users.through)


class FcmConfig(AppConfig):
    name = 'fcm'

    def ready(self):
        from charges.models import Charge
        from fcm.notification import ExpenseNotification
        connect_notification(ExpenseNotification, Charge)
