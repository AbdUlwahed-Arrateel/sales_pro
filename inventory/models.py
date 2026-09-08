from django.db import models
from django.utils import timezone
from accounts.models import User


class Supplier(models.Model):
    owner   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suppliers')
    name    = models.CharField(max_length=200, verbose_name='اسم المورد')
    phone   = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    notes   = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مورد'
        verbose_name_plural = 'الموردون'

    def __str__(self):
        return self.name


class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name  = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'فئة'
        verbose_name_plural = 'الفئات'

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ('piece',    'قطعة'),
        ('kg',       'كيلو'),
        ('liter',    'لتر'),
        ('box',      'علبة'),
        ('cylinder', 'اسطوانة'),
    ]

    owner         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    category      = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    name          = models.CharField(max_length=200, verbose_name='اسم الصنف')
    barcode       = models.CharField(max_length=100, blank=True)
    unit          = models.CharField(max_length=20, choices=UNIT_CHOICES, default='piece')
    retail_price    = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name='سعر القطاعي')
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name='سعر الجملة')
    cost_price      = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name='سعر التكلفة')
    current_stock   = models.DecimalField(max_digits=12, decimal_places=3, default=0, verbose_name='المخزون الحالي')
    min_stock     = models.DecimalField(max_digits=12, decimal_places=3, default=5)
    notes         = models.TextField(blank=True)
    is_active     = models.BooleanField(default=True)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'صنف'
        verbose_name_plural = 'الأصناف'
        ordering = ['name']

    def __str__(self):
        return self.name

    def is_low_stock(self):
        return self.current_stock <= self.min_stock

    def available_stock(self):
        """المخزون المتاح للبيع"""
        return self.current_stock


class Purchase(models.Model):
    """
    شراء: يزيد المخزون الحالي (current_stock) للصنف ويحدّث سعر التكلفة.
    """
    owner         = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    product       = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='purchases')
    supplier      = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='purchases')
    quantity      = models.DecimalField(max_digits=12, decimal_places=3)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=3)
    total_cost    = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    purchase_date = models.DateField(default=timezone.now)
    notes         = models.TextField(blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مشتريات'
        verbose_name_plural = 'المشتريات'
        ordering = ['-purchase_date']

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.purchase_price
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            p = self.product
            p.current_stock += self.quantity
            p.cost_price = self.purchase_price
            p.save()

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'



