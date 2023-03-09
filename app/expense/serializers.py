"""
Serializers for Expense API
"""
from datetime import date

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
