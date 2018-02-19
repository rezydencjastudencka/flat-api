import datetime
from django.contrib.auth.models import User
from django.test import TestCase

from charges.models import Charge


class UTF8ChargeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create()

    def test_create_charge(self):
        charge_title = "Zażółć gęślą jaźń"
        charge = Charge(name=charge_title, date=datetime.date.today(), raw_amount='1', from_user=self.user)
        charge.save()
        self.assertEqual(charge.name, charge_title)
