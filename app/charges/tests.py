import datetime
from django.contrib.auth.models import User
from django.test import TestCase

from charges.models import Charge
from transfers.models import Transfer


class UTF8ChargeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create()

    def test_create_charge(self):
        charge_title = "Zażółć gęślą jaźń"
        charge = Charge(name=charge_title, date=datetime.date.today(), raw_amount='1', from_user=self.user)
        charge.save()
        self.assertEqual(charge.name, charge_title)


class TransferTestCase(TestCase):
    def setUp(self):
        self.fetching_user = User.objects.create_user("fetching_user")
        self.other_user = User.objects.create_user("other_user")

    def test_get_user_transfers_should_return_transfer_to_user(self):
        transfer = Transfer(name="transfer to user", amount=123,
                            date=datetime.date(2018, 11, 20),
                            from_user=self.other_user, to_user=self.fetching_user)
        transfer.save()
        fetched_transfers = Transfer.get_user_transfers(2018, 11, self.fetching_user)
        self.assertListEqual([t.id for t in fetched_transfers], [transfer.id])

    def test_get_user_transfers_should_return_transfer_from_user(self):
        transfer = Transfer(name="transfer from user", amount=123,
                            date=datetime.date(2018, 11, 20),
                            from_user=self.fetching_user, to_user=self.other_user)
        transfer.save()
        fetched_transfers = Transfer.get_user_transfers(2018, 11, self.fetching_user)
        self.assertListEqual([t.id for t in fetched_transfers], [transfer.id])

    def test_get_user_transfers_should_not_return_other_user_transfer(self):
        transfer = Transfer(name="transfer from user", amount=123,
                            date=datetime.date(2018, 11, 20),
                            from_user=self.other_user, to_user=self.other_user)
        transfer.save()
        fetched_transfers = Transfer.get_user_transfers(2018, 11, self.fetching_user)
        self.assertListEqual([t.id for t in fetched_transfers], [])

    def test_get_user_transfers_should_not_return_transfer_outside_month_requested(self):
        transfer_before = Transfer(name="transfer from user", amount=123,
                                   date=datetime.date(2018, 10, 20),
                                   from_user=self.fetching_user,
                                   to_user=self.fetching_user)
        transfer_before.save()

        transfer_after = Transfer(name="transfer from user", amount=123,
                                  date=datetime.date(2018, 12, 20),
                                  from_user=self.fetching_user,
                                  to_user=self.fetching_user)
        transfer_after.save()

        fetched_transfers = Transfer.get_user_transfers(2018, 11, self.fetching_user)
        self.assertListEqual([t.id for t in fetched_transfers], [])

    def test_get_user_transfers_should_not_return_transfer_outside_year_requested(self):
        transfer_before = Transfer(name="transfer from user", amount=123,
                                   date=datetime.date(2017, 11, 20),
                                   from_user=self.fetching_user,
                                   to_user=self.fetching_user)
        transfer_before.save()

        transfer_after = Transfer(name="transfer from user", amount=123,
                                  date=datetime.date(2019, 11, 20),
                                  from_user=self.fetching_user,
                                  to_user=self.fetching_user)
        transfer_after.save()

        fetched_transfers = Transfer.get_user_transfers(2018, 11, self.fetching_user)
        self.assertListEqual([t.id for t in fetched_transfers], [])
