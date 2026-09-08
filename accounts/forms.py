from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Role


class LoginForm(forms.Form):
    username = forms.CharField(
        label='اسم المستخدم',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المستخدم'})
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'كلمة المرور'})
    )


class UserCreateForm(UserCreationForm):
    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone', 'role', 'password1', 'password2']
        labels = {
            'username':   'اسم المستخدم',
            'first_name': 'الاسم الأول',
            'last_name':  'اسم العائلة',
            'email':      'البريد الإلكتروني',
            'phone':      'رقم الهاتف',
            'role':       'الدور الوظيفي',
        }
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'role':       forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].label = 'تأكيد كلمة المرور'
        self.fields['role'].required = True
        if owner:
            self.fields['role'].queryset = Role.objects.filter(owner=owner)
        else:
            self.fields['role'].queryset = Role.objects.none()


class UserEditForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'role', 'is_active']
        labels = {
            'first_name': 'الاسم الأول',
            'last_name':  'اسم العائلة',
            'email':      'البريد الإلكتروني',
            'phone':      'رقم الهاتف',
            'role':       'الدور الوظيفي',
            'is_active':  'الحساب نشط',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control'}),
            'role':       forms.Select(attrs={'class': 'form-select'}),
            'is_active':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, owner=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].required = True
        if owner:
            self.fields['role'].queryset = Role.objects.filter(owner=owner)
        else:
            self.fields['role'].queryset = Role.objects.none()


class ProfileForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'phone']
        labels = {
            'first_name': 'الاسم الأول',
            'last_name':  'اسم العائلة',
            'email':      'البريد الإلكتروني',
            'phone':      'رقم الهاتف',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الاسم الأول'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم العائلة'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@email.com'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0912345678'}),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        exclude = ['owner', 'is_system', 'created_at']
        labels = {
            'name': 'اسم الدور',
            'can_manage_users':      'إدارة الموظفين والأدوار',
            'can_delete_records':    'حذف السجلات (فواتير/أصناف/زبائن/موردون)',
            'can_view_reports':      'عرض التقارير المالية',
            'can_add_customer':      'إضافة زبائن',
            'can_edit_customer':     'تعديل بيانات الزبائن',
            'can_delete_customer':   'حذف زبائن',
            'can_view_all_customers':'عرض جميع الزبائن',
            'can_add_product':       'إضافة أصناف',
            'can_edit_product':      'تعديل الأصناف',
            'can_delete_product':    'حذف أصناف',
            'can_manage_purchases':  'إدارة المشتريات والموردين',
            'can_add_sale':          'إنشاء فواتير بيع',
            'can_delete_sale':       'حذف فواتير',
            'can_add_expense':       'إضافة مصروفات',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: محاسب'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'name':
                field.widget.attrs['class'] = 'form-check-input'
