"""
Tests for Expense API
"""
import datetime
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Expense

from expense.serializers import ExpenseSerializer


EXPENSE_URL = reverse('expense:expense-list')
EXPENSE_SUMMARY_URL = reverse('expense:expense-summary')


def detail_url(expense_id):
    return reverse('expense:expense-detail', args=[expense_id])


def create_expense_payload():
    return {
        'expense_name': 'Groceries',
        'price': Decimal('1000.00'),
        'date_created': date.today(),
        'category': 'Food'
    }


def create_expense(user, **params):
    defaults = create_expense_payload()

    defaults.update(params)

    expense = Expense.objects.create(user=user, **defaults)
    return expense


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def create_user_payload():
    return {
        'email': 'test@example.com',
        'password': 'test1234',
        'name': 'Test'
    }


def last_month_date():
    today_date = datetime.date.today()
    last_month = today_date.replace(day=1) - datetime.timedelta(days=1)
    return last_month


class PublicExpenseApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(EXPENSE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateExpenseApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(**create_user_payload())
        self.client.force_authenticate(self.user)

    def test_retrieve_expenses(self):
        create_expense(user=self.user)
        create_expense(user=self.user)

        res = self.client.get(EXPENSE_URL)

        expenses = Expense.objects.all().order_by('-date_created')
        serializer = ExpenseSerializer(expenses, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_expense_list_limited_to_user(self):
        other_user = create_user(
            email='other@example.com',
            password='root1234'
        )
        create_expense(user=other_user)
        create_expense(user=self.user)

        res = self.client.get(EXPENSE_URL)

        expenses = Expense.objects.filter(user=self.user)
        serializer = ExpenseSerializer(expenses, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_expense_blank_date(self):
        payload = {
            'expense_name': 'Expense',
            'price': Decimal('1000.00')
        }

        res = self.client.post(EXPENSE_URL, payload)

        expense = Expense.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(expense, k), v)
        self.assertEqual(expense.user, self.user)
        self.assertEqual(expense.date_created, date.today())
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_expense_given_date(self):
        payload = {
            'expense_name': 'Expense',
            'price': Decimal('1000.00'),
            'date_created': datetime.date(2023, 2, 13)
        }

        res = self.client.post(EXPENSE_URL, payload)

        expense = Expense.objects.get(id=res.data['id'])

        for k, v in payload.items():
            self.assertEqual(getattr(expense, k), v)
        self.assertEqual(expense.user, self.user)
        self.assertEqual(expense.date_created, payload['date_created'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_get_all_expenses_per_category(self):
        create_expense(user=self.user)
        create_expense(user=self.user, **{'category': 'Wants'})
        create_expense(user=self.user, **{'category': 'Wants'})

        res = self.client.get(EXPENSE_URL, {'category': 'Wants'})

        self.assertEqual(res.data[0]['category'], 'Wants')
        self.assertEqual(res.data[1]['category'], 'Wants')
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_expense(self):
        expense = create_expense(user=self.user)

        res = self.client.delete(detail_url(expense.id))

        expenses = Expense.objects.filter(user=self.user)

        self.assertFalse(expenses.exists())
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_sum_per_category(self):
        create_expense(user=self.user)
        create_expense(user=self.user)
        create_expense(user=self.user, **{'category': 'Wants'})
        create_expense(user=self.user, **{'category': 'Food'})
        create_expense(user=self.user, **{'category': 'Food',
                                          'date_created': last_month_date()})

        res = self.client.get(EXPENSE_SUMMARY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['user'], self.user.email)
        self.assertEqual(len(res.data['summary']), 2)
        self.assertEqual(len(res.data['summary'][0]['expense_total']), 1)
        self.assertEqual(len(res.data['summary'][1]['expense_total']), 2)
