"""
Service layer for Expense Summary
"""
from django.db.models.functions import TruncMonth
from django.db.models import Sum

from collections import defaultdict


def expense_summary(user, queryset):

    expenses_by_category = filter_expense_by_category(user, queryset)

    totals_by_month = group_expense_per_month(expenses_by_category)

    return {
        'user': user.email,
        'summary': build_summary(totals_by_month)
    }


def filter_expense_by_category(user, queryset):
    """
    Get total_price of `Expenses` of the same category and month_created
    :param user:
    :param queryset:
    :return:
    """
    return queryset.filter(user=user)\
                   .annotate(month_created=TruncMonth('date_created'))\
                   .values('category', 'month_created')\
                   .annotate(total_price=Sum('price'))\
                   .order_by('category', 'month_created')


def group_expense_per_month(expenses_by_category):
    """
    Group all total_spending per category by month_created
    :param expenses_by_category:
    :return:
    """
    totals_by_month = defaultdict(list)

    for expense in expenses_by_category:
        month_created = expense['month_created'].strftime('%B-%Y')

        totals_by_month[month_created].append({
            'category': expense['category'],
            'total_spending': str(expense['total_price'])
        })

    return totals_by_month


def build_summary(totals_by_month):
    """
    Create a list of expense_total per month_created
    :param totals_by_month:
    :return:
    """
    serialized_output = []
    for month_created, category_sums in totals_by_month.items():
        serialized_output.append({
            'month': month_created,
            'expense_total': category_sums
        })

    return serialized_output
