from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken import models as Token

from expenses.models import ExpenseUser, Expense, ExpensePaidBy, ExpenseOwedBy
from expenses.serializers import (
    ExpenseUserSerializer,
    ExpenseSerializer,
)
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404


@api_view(["POST"])
def user_register(request):
    serializer = ExpenseUserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.password = make_password(request.data.get("password"))
        user.save()
        token = Token.Token.objects.create(user=user)
        return Response(
            {"message": "User registered, token created", "token": token.key}
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def user_login(request):
    user = get_object_or_404(ExpenseUser, email=request.data.get("email"))
    if not user.check_password(request.data.get("password")):
        return Response(
            {"message": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED
        )
    token = Token.Token.objects.get(user=user)
    return Response({"message": "User logged in successfully", "token": token.key})


@api_view(["GET"])
def user_get(request, user_id):
    user = get_object_or_404(ExpenseUser, id=user_id)
    user_serializer = ExpenseUserSerializer(user)
    return Response(
        {"message": "User fetched successfully", "data": user_serializer.data}
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def expense_add(request):
    serializer = ExpenseSerializer(data=request.data, context={"request": request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Check if the sum of paid amount is equal to the total amount
    if sum(request.data.get("paidBy").values()) != request.data.get("amount"):
        return Response(
            {"message": "Sum of paid amount should be equal to total amount"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if the amount/percentage is greater than 0
    for user_id, val in request.data.get("paidBy").items():
        if val < 0:
            return Response(
                {"message": "Amount/Percentage should be greater than 0"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    expenseType = request.data.get("expenseType")

    if expenseType == "PERCENT":
        # Check if the sum of percentages is 100
        if sum(request.data.get("owedBy").values()) != 100:
            return Response(
                {"message": "Sum of percentages should be 100"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    elif expenseType == "EXACT":
        # Check if the sum of amounts in owedBy is equal to the total amount
        if sum(request.data.get("owedBy").values()) != request.data.get("amount"):
            return Response(
                {"message": "Sum of amounts should be equal to the total amount"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    # Create the expense after all validations to avoid inconsistent data
    expense = serializer.save()

    for user_id, val in request.data.get("paidBy").items():
        paid_by = ExpensePaidBy.objects.create(
            # It can be optimized by using ids directly instead of fetching the objects
            expenseId=Expense.objects.get(expenseId=expense.expenseId),
            userId=ExpenseUser.objects.get(id=user_id),
            amount=val,
        )
        paid_by.save()

    if expenseType == "EQUAL":
        total_users_owed = len(request.data.get("owedBy"))
        total_amount = request.data.get("amount")
        for user_id in request.data.get("owedBy"):
            owed_by = ExpenseOwedBy.objects.create(
                # It can be optimized by using ids directly instead of fetching the objects
                expenseId=Expense.objects.get(expenseId=expense.expenseId),
                userId=ExpenseUser.objects.get(id=user_id),
                amount=total_amount / total_users_owed,
            )
            owed_by.save()

    elif expenseType == "PERCENT":
        for user_id, percent in request.data.get("owedBy").items():
            owed_by = ExpenseOwedBy.objects.create(
                # It can be optimized by using ids directly instead of fetching the objects
                expenseId=Expense.objects.get(expenseId=expense.expenseId),
                userId=ExpenseUser.objects.get(id=user_id),
                amount=request.data.get("amount") * percent / 100,
            )
            owed_by.save()

    elif expenseType == "EXACT":
        for user_id, val in request.data.get("owedBy").items():
            owed_by = ExpenseOwedBy.objects.create(
                # It can be optimized by using ids directly instead of fetching the objects
                expenseId=Expense.objects.get(expenseId=expense.expenseId),
                userId=ExpenseUser.objects.get(id=user_id),
                amount=val,
            )
            owed_by.save()
    else :
        return Response(
            {"message": "Invalid expense type"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"message": "Expense added successfully"})


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def balance_sheet_get(request):
    return Response({"message": "Expenses fetched successfully"})


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def balance_sheet_get_all(request):
    return Response({"message": "Expenses fetched successfully"})


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def balance_sheet_get_all_pdf(request):
    return Response({"message": "Expenses pdf fetched successfully"})
