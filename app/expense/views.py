"""
Views for Expense API
"""
from rest_framework import viewsets
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
        expense_name = self.request.query_params.get('expense_name')

        if expense_name:
            queryset = queryset.filter(expense_name=expense_name)

        return queryset.order_by('-date_created')

    def perform_create(self, serializer):
        """
        Create new Expense
        :param serializer:
        :return:
        """
        serializer.save(user=self.request.user)
