from django.db import models
from accounts.models import User


class Customer(models.Model):
    ACTIVITY_CHOICES = [
        ('retail', 'قطاعي'),
        ('wholesale', 'جملة'),
        ('both', 'جملة وقطاعي'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers', verbose_name='المالك')
    name = models.CharField(max_length=200, verbose_name='اسم الزبون')
    business_name = models.CharField(max_length=200, blank=True, verbose_name='اسم النشاط')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, default='retail', verbose_name='نوع النشاط')
    address = models.TextField(blank=True, verbose_name='العنوان')
    personal_phone = models.CharField(max_length=20, blank=True, verbose_name='الهاتف الشخصي')
    business_phone = models.CharField(max_length=20, blank=True, verbose_name='هاتف النشاط')
    notes = models.TextField(blank=True, verbose_name='ملاحظات')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'زبون'
        verbose_name_plural = 'الزبائن'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_balance(self):
        """Calculate current balance (unpaid amount)"""
        from sales.models import Invoice
        from django.db.models import Sum
        total = Invoice.objects.filter(customer=self).aggregate(
            total=Sum('total_amount'), paid=Sum('paid_amount')
        )
        return (total['total'] or 0) - (total['paid'] or 0)

    def get_buying_power(self):
        """Calculate buying power movements"""
        from sales.models import Invoice
        from django.db.models import Sum
        return Invoice.objects.filter(customer=self).aggregate(
            total=Sum('total_amount')
        )['total'] or 0
