from django.db import models
from django.core.validators import EmailValidator
from .validators import validate_phone_number


"""CREATED TO STRICTLY ADHERE TO THE GIVEN SPECS 
    OTHERWISE DJANGO USER CLASS WILL HAVE BEEN USED"""
class User(models.Model):
    userId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=False)
    password = models.CharField(max_length=255, blank=False)
    email = models.EmailField(max_length=255, unique=True, blank=False ,validators=[EmailValidator])
    phone = models.CharField(max_length=10, blank=False , validators=[validate_phone_number])
    createdAt = models.DateTimeField(auto_now_add=True)


class Expense(models.Model):
    expenseId = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=255, blank=False)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
    createdById = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)


class ExpensePaidBy(models.Model):
    expenseId = models.ForeignKey(Expense, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)

    class Meta:
        unique_together = (("expenseId", "userId"),)


class ExpenseOwedBy(models.Model):
    expenseId = models.ForeignKey(Expense, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)

    class Meta:
        unique_together = (("expenseId", "userId"),)
