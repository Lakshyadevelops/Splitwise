from django.shortcuts import render
from rest_framework.decorators import api_view
from expenses import models

# Create your views here.


@api_view(["POST"])
def register_user(request):
    pass


@api_view(["GET"])
def get_user(request):
    pass


@api_view(["POST"])
def add_expense(request):
    pass


@api_view(["POST"])
def user_login(request):
    pass
