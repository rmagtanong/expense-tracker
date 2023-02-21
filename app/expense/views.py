"""
Views for Expense API
"""
from django.db.models import Sum

from rest_framework import viewsets, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Expense
from expense import serializers


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    View for manage Expense APIs
    """
    serializer_class = serializers.ExpenseSerializer
    queryset = Expense.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieve Expenses for authenticated User
        :return:
        """
        queryset = self.queryset.filter(user=self.request.user)
        category = self.request.query_params.get('category')

        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by('-date_created')

    def perform_create(self, serializer):
        """
        Create new Expense
        :param serializer:
        :return:
        """
        serializer.save(user=self.request.user)

#
# class ExpenseSummaryViewSet(ExpenseViewSet):
#     serializer_class = serializers.ExpenseSerializer
#     queryset = Expense.objects.all()
#
#     def get_queryset(self):
#         return self.queryset
