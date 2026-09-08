from django import forms
from .models import Product, Purchase, Supplier, Category


class ProductForm(forms.ModelForm):
    """نموذج إضافة صنف جديد — المعلومات الأساسية فقط، بدون سعر أو كمية"""
    class Meta:
        model = Product
        fields = ['name', 'barcode', 'category', 'unit', 'min_stock', 'notes']
        widgets = {
            'name':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم الصنف'}),
            'barcode':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اختياري'}),
            'category':  forms.Select(attrs={'class': 'form-select'}),
            'unit':      forms.Select(attrs={'class': 'form-select'}),
            'min_stock': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'placeholder': '5'}),
            'notes':     forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        if owner:
            self.fields['category'].queryset = Category.objects.filter(owner=owner)


class ProductPricingForm(forms.ModelForm):
    """نموذج تعديل أسعار صنف موجود"""
    class Meta:
        model = Product
        fields = ['retail_price', 'wholesale_price', 'cost_price', 'min_stock']
        widgets = {
            'retail_price':    forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'wholesale_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'cost_price':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'min_stock':       forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
        }


class PurchaseForm(forms.ModelForm):
    new_retail_price = forms.DecimalField(
        required=False, max_digits=12, decimal_places=3,
        label='سعر البيع القطاعي الجديد (اختياري)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'step': '0.001',
            'placeholder': 'اتركه فارغاً لعدم تغيير السعر الحالي'
        })
    )
    new_wholesale_price = forms.DecimalField(
        required=False, max_digits=12, decimal_places=3,
        label='سعر البيع بالجملة الجديد (اختياري)',
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 'step': '0.001',
            'placeholder': 'اتركه فارغاً لعدم تغيير السعر الحالي'
        })
    )

    class Meta:
        model = Purchase
        fields = ['product', 'supplier', 'quantity', 'purchase_price', 'purchase_date', 'notes']
        widgets = {
            'product':       forms.Select(attrs={'class': 'form-select'}),
            'supplier':      forms.Select(attrs={'class': 'form-select'}),
            'quantity':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'purchase_price':forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes':         forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        if owner:
            self.fields['product'].queryset = Product.objects.filter(owner=owner, is_active=True)
            self.fields['supplier'].queryset = Supplier.objects.filter(owner=owner)
        # إعادة ترتيب الحقول: سعر التكلفة ثم أسعار البيع الاختيارية معاً
        self.order_fields([
            'product', 'supplier', 'quantity', 'purchase_price',
            'new_retail_price', 'new_wholesale_price', 'purchase_date', 'notes'
        ])


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'address', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'})}