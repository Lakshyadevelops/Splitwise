from .models import ExpenseUser, Expense, ExpensePaidBy, ExpenseOwedBy

from rest_framework import serializers


class ExpenseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExpenseUser
        fields = ["name", "email", "phone", "createdAt", "password"]
        read_only_fields = ["createdAt"]
        extra_kwargs = {
            'password': {'write_only': True}  # Ensure password is write-only
        }


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["expenseId", "desc", "amount", "createdById", "createdAt"]
        read_only_fields = ["createdById", "createdAt"]

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["createdById"] = user
        return super().create(validated_data)


class ExpensePaidBySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpensePaidBy
        fields = ["expenseId", "userId", "amount"]


class ExpenseOwedBySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseOwedBy
        fields = ["expenseId", "userId", "amount"]
