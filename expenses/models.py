from django.db import models

# Create your models here.


class User(models.Model):
    userId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=10)
    createdAt = models.DateTimeField(auto_now_add=True)


class Expense(models.Model):
    expenseId = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    createdById = models.ForeignKey(User, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)


class ExpensePaidBy(models.Model):
    expenseId = models.ForeignKey(Expense, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = (("expenseId", "userId"),)


class ExpenseOwedBy(models.Model):
    expenseId = models.ForeignKey(Expense, on_delete=models.CASCADE)
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = (("expenseId", "userId"),)
