from django.contrib import admin
from django.urls import path
from expenses import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/user/register", views.user_register),
    path("api/v1/user/login/", views.user_login),
    path("api/v1/user/<int:user_id>/", views.user_get),
    path("api/v1/expense/", views.expense_add),
    path("api/v1/balance-sheet/<int:user_id>/", views.balance_sheet_get),
    path("api/v1/balance-sheet/", views.balance_sheet_get_all),
    path("api/v1/balance-sheet-pdf/", views.balance_sheet_get_all_pdf),
]
