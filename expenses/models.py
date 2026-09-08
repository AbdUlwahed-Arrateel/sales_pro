from django.db import models
from accounts.models import User
from django.utils import timezone


class ExpenseCategory(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=100, verbose_name='اسم الفئة')
    icon = models.CharField(max_length=50, default='💰')

    class Meta:
        verbose_name = 'فئة مصروف'
        verbose_name_plural = 'فئات المصروفات'

    def __str__(self):
        return self.name


class Expense(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='الفئة')
    description = models.CharField(max_length=300, verbose_name='الوصف')
    amount = models.DecimalField(max_digits=14, decimal_places=3, verbose_name='المبلغ')
    date = models.DateField(default=timezone.now, verbose_name='التاريخ')
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مصروف'
        verbose_name_plural = 'المصروفات'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f'{self.description} - {self.amount}'
