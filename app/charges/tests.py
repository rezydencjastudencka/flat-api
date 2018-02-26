import datetime

import json
from django.contrib.auth.models import User
from django.test import TestCase
from django.test import Client

from charges.models import Charge


class UTF8ChargeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create()

    def test_create_charge(self):
        charge_title = "Zażółć gęślą jaźń"
        charge = Charge(name=charge_title, date=datetime.date.today(), raw_amount='1', from_user=self.user)
        charge.save()
        self.assertEqual(charge.name, charge_title)


class CreateChargeTestCase(TestCase):
    def test_call_create_denies_anonymous(self):
        client = Client()
        response = client.post('/charge/create')
        self.assertEqual(response.status_code, 403)


class AuthenticatedCreateChargeTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1')
        self.user2 = User.objects.create_user(username='user2')

        self.valid_charge = {
            'to': [self.user2.id],
            'date': '2018-03-30T01:02:03.2Z',
            'name': 'test charge',
            'rawAmount': '2+2.5',
        }

        self.client = Client()
        self.client.force_login(self.user1)

    def submit(self, data):
        return self.client.post('/charge/create', content_type='application/json', data=json.dumps(data))

    def replace_value_in_valid(self, key, value):
        data = dict(self.valid_charge)
        data[key] = value
        return data

    def test_call_create_require_json(self):
        response = self.client.post('/charge/create', self.valid_charge)
        self.assertEqual(response.status_code, 415)

    def test_call_create_requires_data(self):
        def remove_key(key):
            charge_without_field = dict(self.valid_charge)
            del charge_without_field[key]
            return charge_without_field

        def remove_single_key(valid_data):
            return [remove_key(key) for key in valid_data]

        invalid_requests = remove_single_key(self.valid_charge)

        for request in invalid_requests:
            self.assertEqual(self.submit(request).status_code, 400, request)

    def test_call_create_returns_calculated_amount(self):
        response = self.submit(self.replace_value_in_valid('rawAmount', '2*(6+10)'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['amount'], 32)

    def test_call_create_fails_with_invalid_raw_amount(self):
        data_with_invalid_raw_amount = self.replace_value_in_valid('rawAmount', '1 + invalid math')
        self.assertEqual(self.submit(data_with_invalid_raw_amount).status_code, 400)

    def test_call_create_fails_with_invalid_user(self):
        nonexistent_user_id = 999
        data_with_nonexistent_user = self.replace_value_in_valid('to', [nonexistent_user_id])
        self.assertEqual(self.submit(data_with_nonexistent_user).status_code, 400)

    def test_call_create_returns_charge(self):
        response = self.submit(self.valid_charge).json()
        self.assertEqual(response['date'], '2018-03-30')  # timestamp lost, only date preserved(?)
        self.assertEqual(response['name'], self.valid_charge['name'])
        self.assertEqual(response['rawAmount'], self.valid_charge['rawAmount'])
        self.assertEqual(response['amount'], 4.5)

        self.assertEqual(response['to'][0]['id'], self.valid_charge['to'][0])
        self.assertEqual(response['to'][0]['name'], self.user2.username)
