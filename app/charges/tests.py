import datetime
from django.contrib.auth.models import User
from django.test import TestCase

from charges.models import Charge, Flat, Profile
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


class ChargesSummaryTestCase(TestCase):
    def setUp(self):
        self.fetching_user_flat = Flat.objects.create(name="fetching_user_flat")
        self.other_flat = Flat.objects.create(name="other_flat")
        self.fetching_user = User.objects.create_user("fetching_user")
        Profile.objects.create(flat=self.fetching_user_flat, user=self.fetching_user)
        self.same_flat_user = User.objects.create_user("user_in_same_flat")
        Profile.objects.create(flat=self.fetching_user_flat, user=self.same_flat_user)
        self.other_flat_user = User.objects.create_user("user_in_other_flat")
        Profile.objects.create(flat=self.other_flat, user=self.other_flat_user)

    def test_summary_should_return_only_users_in_flat(self):
        summary = Charge.get_summary_new(2018, 12, self.fetching_user)
        self.assertSetEqual(set([e['user'].id for e in summary.values()]),
                            {self.fetching_user.id, self.same_flat_user.id})

    def test_summary_should_return_user_from_other_flat_if_charge_from_him_exists(self):
        charge = Charge(name="charge from other flat user", raw_amount="123",
                        date=datetime.date(2018, 12, 20),
                        from_user=self.other_flat_user)

        charge.save()
        charge.to_users.set([self.fetching_user])

        summary = Charge.get_summary_new(2018, 12, self.fetching_user)
        self.assertSetEqual(
            set([e['user'].id for e in summary.values()]),
            {self.fetching_user.id, self.same_flat_user.id, self.other_flat_user.id})

    def test_summary_should_return_user_from_other_flat_if_charge_to_him_exists(self):
        charge = Charge(name="charge to other flat user", raw_amount="123",
                        date=datetime.date(2018, 12, 20),
                        from_user=self.fetching_user)

        charge.save()
        charge.to_users.set([self.other_flat_user])

        summary = Charge.get_summary_new(2018, 12, self.fetching_user)
        self.assertSetEqual(
            set([e['user'].id for e in summary.values()]),
            {self.fetching_user.id, self.same_flat_user.id, self.other_flat_user.id})
