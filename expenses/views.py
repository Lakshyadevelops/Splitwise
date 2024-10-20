from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from expenses import models


@api_view(["POST"])
def user_register(request):
    return Response({"message": "User registered successfully"})


@api_view(["GET"])
def user_get(request):
    return Response({"message": "User retrieved successfully"})


@api_view(["POST"])
def expense_add(request):
    return Response({"message": "Expense added successfully"})


@api_view(["POST"])
def user_login(request):
    return Response({"message": "User logged in successfully"})
