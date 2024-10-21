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
from django.db.models import Sum, F, DecimalField, OuterRef, Subquery
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa


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
    else:
        return Response(
            {"message": "Invalid expense type"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response({"message": "Expense added successfully"})


def get_expenses_with_net_transaction(user_id):
    # Subquery to sum paid amounts for each expense
    paid_subquery = (
        ExpensePaidBy.objects.filter(expenseId=OuterRef("pk"), userId=user_id)
        .values("expenseId")
        .annotate(total_paid=Sum("amount"))
        .values("total_paid")
    )

    # Subquery to sum owed amounts for each expense
    owed_subquery = (
        ExpenseOwedBy.objects.filter(expenseId=OuterRef("pk"), userId=user_id)
        .values("expenseId")
        .annotate(total_owed=Sum("amount"))
        .values("total_owed")
    )

    # Annotate total paid, total owed, and calculate net_transaction
    expenses = (
        Expense.objects.annotate(
            total_paid=Subquery(paid_subquery, output_field=DecimalField()),
            total_owed=Subquery(owed_subquery, output_field=DecimalField()),
            # Calculate net transaction: total paid - total owed (with default value 0 if None)
            net_transaction=(F("total_paid") - F("total_owed")),
        )
        .order_by("createdAt")
        .values("expenseId", "desc", "amount", "createdAt", "net_transaction")
    )

    return list(expenses)


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def balance_sheet_get(request, user_id):
    total_paid = (
        ExpensePaidBy.objects.filter(userId_id=user_id).aggregate(
            total_paid=Sum("amount")
        )["total_paid"]
        or 0
    )
    total_owed = (
        ExpenseOwedBy.objects.filter(userId_id=user_id).aggregate(
            total_owed=Sum("amount")
        )["total_owed"]
        or 0
    )
    total_balance = total_paid - total_owed

    transactions = get_expenses_with_net_transaction(user_id)

    return Response(
        {
            "message": "Expenses fetched successfully",
            "user_id": user_id,
            "total_paid": total_paid,
            "total_owed": total_owed,
            "total_balance": total_balance,
            "data": transactions,
        }
    )


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def balance_sheet_get_all(request):
    users = ExpenseUser.objects.all()
    userData = {}
    for user in users:
        total_paid = (
            ExpensePaidBy.objects.filter(userId_id=user.id).aggregate(
                total_paid=Sum("amount")
            )["total_paid"]
            or 0
        )
        total_owed = (
            ExpenseOwedBy.objects.filter(userId_id=user.id).aggregate(
                total_owed=Sum("amount")
            )["total_owed"]
            or 0
        )
        transaction = get_expenses_with_net_transaction(user.id)
        userData[user.id] = {
            "user_id": user.id,
            "total_paid": total_paid,
            "total_owed": total_owed,
            "total_balance": total_paid - total_owed,
            "transactions": transaction,
        }
    return Response({"message": "Expenses fetched successfully", "data": userData})


def render_to_pdf(template_src, context_dict={}):
    template = render_to_string(template_src, context_dict)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="balance_sheet.pdf"'

    pisa_status = pisa.CreatePDF(template, dest=response)

    if pisa_status.err:
        return HttpResponse(f"We had some errors with code {pisa_status.err}")

    return response


@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@api_view(["GET"])
def balance_sheet_get_all_pdf(request):
    users = ExpenseUser.objects.all()
    userData = []
    for user in users:
        total_paid = (
            ExpensePaidBy.objects.filter(userId_id=user.id).aggregate(
                total_paid=Sum("amount")
            )["total_paid"]
            or 0
        )
        total_owed = (
            ExpenseOwedBy.objects.filter(userId_id=user.id).aggregate(
                total_owed=Sum("amount")
            )["total_owed"]
            or 0
        )
        transaction = get_expenses_with_net_transaction(user.id)
        userData.append(
            {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "total_paid": total_paid,
                "total_owed": total_owed,
                "total_balance": total_paid - total_owed,
                "transactions": transaction,
            }
        )

    context = {"data": userData}

    return render_to_pdf("balance_sheet_template.html", context)
