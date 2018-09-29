import datetime
from unittest import mock
from unittest.mock import Mock

from django.contrib.auth.models import User
from django.test import TestCase

from charges.models import Charge


class NewChargeNotificationTests(TestCase):
    def setUp(self):
        self.charge_creator = User.objects.create_user('charge_creator', 'pass')
        self.target_user1 = User.objects.create_user('notified_user', 'pass')
        self.target_user2 = User.objects.create_user('notified_user2', 'pass')

    @mock.patch('fcm.signals.notify_new_charge', Mock(side_effect=IOError))
    def test_failed_notification(self):
        """Ensure failed FCM message delivery does not raise exception causing transaction rollback."""
        charge = Charge(name="new charge", date=datetime.date.today(), raw_amount='1', from_user=self.charge_creator)
        charge.save()
        charge.to_users.add(self.target_user1)

    def test_notification_skip_creator(self):
        charge = Charge(name="new charge", date=datetime.date.today(), raw_amount='1', from_user=self.charge_creator)
        charge.save()
        recipient_ids = {self.charge_creator.id, self.target_user1.id, self.target_user2.id}
        charge.to_users.set(recipient_ids)

        self.assertNotIn(self.charge_creator.id, get_notif_users(charge, recipient_ids))
