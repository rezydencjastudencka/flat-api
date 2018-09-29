import datetime
import logging
from unittest import mock
from unittest.mock import Mock

from django.contrib.auth.models import User
from django.test import TestCase

from charges.models import Charge
from fcm.notification import ExpenseNotification


class NewExpenseNotificationTest(TestCase):
    def setUp(self):
        self.charge_creator = User.objects.create_user('charge_creator', 'pass')
        self.target_user1 = User.objects.create_user('notified_user', 'pass')
        self.target_user2 = User.objects.create_user('notified_user2', 'pass')

    def create_charge(self, recipient_ids):
        charge = Charge(name="new charge", date=datetime.date.today(), raw_amount='1', from_user=self.charge_creator)
        charge.save()
        charge.to_users.set(recipient_ids)
        return charge

    @mock.patch('fcm.notification.Notification.send', Mock(side_effect=IOError))
    def test_failed_notification(self):
        """Ensure failed FCM message delivery does not raise exception causing transaction rollback."""
        self.create_charge({self.target_user1})

    def test_notification_skip_creator(self):
        recipient_ids = {self.charge_creator.id, self.target_user1.id, self.target_user2.id}
        charge = self.create_charge(recipient_ids)
        notification = ExpenseNotification(charge, recipient_ids)

        self.assertNotIn(self.charge_creator.id, notification.recipient_ids)
