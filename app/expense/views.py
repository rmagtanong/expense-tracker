"""
Views for Expense API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Expense
from expense import serializers
from expense.summary import expense_summary


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
        Retrieve `Expenses` for authenticated `User`, can pass a query string
        `category` to get `Expenses` only for a specific category
        :return:
        """
        queryset = self.queryset.filter(user=self.request.user)
        category = self.request.query_params.get('category')

        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by('-date_created')

    def perform_create(self, serializer):
        """
        Create new `Expense`
        :param serializer:
        :return:
        """
        serializer.save(user=self.request.user)

    @action(detail=False)
    def summary(self, request, *args, **kwargs):
        return Response(expense_summary(self.request.user, self.queryset))
