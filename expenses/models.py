from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import EmailValidator
from .validators import validate_phone_number


class ExpenseUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashes the password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class ExpenseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        max_length=255, unique=True, blank=False, validators=[EmailValidator]
    )
    name = models.CharField(max_length=255, blank=False)
    phone = models.CharField(
        max_length=10, blank=False, validators=[validate_phone_number]
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone"]
    objects = ExpenseUserManager()

    def __str__(self):
        return self.email


class Expense(models.Model):
    expenseId = models.AutoField(primary_key=True)
    desc = models.CharField(max_length=255, blank=False)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)
    createdById = models.ForeignKey(ExpenseUser, on_delete=models.CASCADE)
    createdAt = models.DateTimeField(auto_now_add=True)


class ExpensePaidBy(models.Model):
    expenseId = models.ForeignKey(Expense, on_delete=models.CASCADE)
    userId = models.ForeignKey(ExpenseUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)

    class Meta:
        unique_together = (("expenseId", "userId"),)
        indexes = [
            models.Index(fields=["userId"]),
        ]


class ExpenseOwedBy(models.Model):
    expenseId = models.ForeignKey(Expense, on_delete=models.CASCADE)
    userId = models.ForeignKey(ExpenseUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=False)

    class Meta:
        unique_together = (("expenseId", "userId"),)
        indexes = [
            models.Index(fields=["userId"]),
        ]
