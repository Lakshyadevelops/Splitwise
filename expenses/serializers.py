from .models import ExpenseUser, Expense, ExpensePaidBy, ExpenseOwedBy

from rest_framework import serializers


class ExpenseUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    createdAt = serializers.DateTimeField(read_only=True)

    class Meta:
        model = ExpenseUser
        fields = ["name", "email", "phone", "createdAt", "password"]


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["expenseId", "desc", "amount", "createdById", "createdAt"]


class ExpensePaidBySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensePaidBy
        fields = ["expenseId", "userId", "amount"]


class ExpenseOwedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseOwedBy
        fields = ["expenseId", "userId", "amount"]
