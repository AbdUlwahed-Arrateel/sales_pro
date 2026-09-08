from django.db import models
from django.utils import timezone
from accounts.models import User
from customers.models import Customer
from inventory.models import Product


class Invoice(models.Model):
    SALE_TYPE_CHOICES = [('retail', 'قطاعي'), ('wholesale', 'جملة')]
    STATUS_CHOICES = [('paid', 'مدفوعة'), ('partial', 'جزئية'), ('unpaid', 'غير مدفوعة')]

    owner        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    customer     = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    sale_type    = models.CharField(max_length=20, choices=SALE_TYPE_CHOICES, default='retail')
    total_amount = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    discount     = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    paid_amount  = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    notes        = models.TextField(blank=True)
    created_by   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invoices')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'فاتورة'
        verbose_name_plural = 'الفواتير'
        ordering = ['-created_at']

    def __str__(self):
        return f'فاتورة #{self.pk} — {self.customer or "نقد"}'

    def get_balance(self):
        return self.total_amount - self.paid_amount

    def save(self, *args, **kwargs):
        if self.paid_amount >= self.total_amount:
            self.status = 'paid'
        elif self.paid_amount > 0:
            self.status = 'partial'
        else:
            self.status = 'unpaid'
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product     = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity    = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price  = models.DecimalField(max_digits=12, decimal_places=3)
    total_price = models.DecimalField(max_digits=14, decimal_places=3)

    class Meta:
        verbose_name = 'بند'
        verbose_name_plural = 'البنود'

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.product.current_stock -= self.quantity
            self.product.save()


class Payment(models.Model):
    invoice     = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount      = models.DecimalField(max_digits=14, decimal_places=3)
    date        = models.DateTimeField(auto_now_add=True)
    notes       = models.CharField(max_length=200, blank=True)
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'الدفعات'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.db.models import Sum
        total = Payment.objects.filter(invoice=self.invoice).aggregate(t=Sum('amount'))['t'] or 0
        self.invoice.paid_amount = total
        self.invoice.save()
