from django.contrib import admin
from .models import User, Expense, ExpensePaidBy, ExpenseOwedBy

# SINCE WE ARE FOCUSING ON BACKEND APIs NOT DONE ANY CUSTOMIZATION IN ADMIN PANEL

# Register your models here.
admin.site.register(User)
admin.site.register(Expense)
admin.site.register(ExpensePaidBy)
admin.site.register(ExpenseOwedBy)
