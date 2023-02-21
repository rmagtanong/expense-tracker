"""
Serializers for Expense API
"""
from datetime import date

from django.db.models import Sum

from rest_framework import serializers

from core.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = [
            'id',
            'expense_name',
            'price',
            'category',
            'date_created',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):

        if 'date_created' not in validated_data:
            validated_data['date_created'] = date.today()

        expense = Expense.objects.create(**validated_data)
        return expense


# class ExpenseSummarySerializer(serializers.Serializer):
#     category = serializers.CharField()
#     total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
#
#     def to_representation(self, instance):
#         return Expense.objects.values('category').order_by('category').annotate(total_price=Sum('price'))
#
