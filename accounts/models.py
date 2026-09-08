from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """
    دور وظيفي قابل للتخصيص يحدد صلاحيات مجموعة من الموظفين.
    كل صاحب عمل (owner) له أدواره الخاصة، ويمكنه تعديل صلاحيات أي دور
    أو إضافة أدوار جديدة كلياً.
    """
    owner = models.ForeignKey(
        'accounts.User', on_delete=models.CASCADE, related_name='custom_roles',
        verbose_name='صاحب العمل'
    )
    name = models.CharField(max_length=50, verbose_name='اسم الدور')
    is_system = models.BooleanField(
        default=False, verbose_name='دور أساسي',
        help_text='الأدوار الأساسية (مدير/كاشير/مشاهد) تُنشأ تلقائياً، ويمكن تعديل صلاحياتها لكن لا يمكن حذفها'
    )

    # ── صلاحيات هيكلية (إدارية) ──────────────────────────────────
    can_manage_users   = models.BooleanField(default=False, verbose_name='إدارة الموظفين والأدوار')
    can_delete_records = models.BooleanField(default=False, verbose_name='حذف السجلات (فواتير/أصناف/زبائن/موردون)')
    can_view_reports    = models.BooleanField(default=False, verbose_name='عرض التقارير المالية')

    # ── صلاحيات تفصيلية ──────────────────────────────────────────
    can_add_customer       = models.BooleanField(default=False,  verbose_name='إضافة زبائن')
    can_edit_customer      = models.BooleanField(default=False,  verbose_name='تعديل بيانات الزبائن')
    can_delete_customer    = models.BooleanField(default=False, verbose_name='حذف زبائن')
    can_view_all_customers = models.BooleanField(default=False,  verbose_name='عرض جميع الزبائن')
    can_add_product        = models.BooleanField(default=False,  verbose_name='إضافة أصناف')
    can_edit_product       = models.BooleanField(default=False,  verbose_name='تعديل الأصناف')
    can_delete_product     = models.BooleanField(default=False, verbose_name='حذف أصناف')
    can_manage_purchases   = models.BooleanField(default=False, verbose_name='إدارة المشتريات والموردين')
    can_add_sale           = models.BooleanField(default=False,  verbose_name='إنشاء فواتير بيع')
    can_delete_sale        = models.BooleanField(default=False, verbose_name='حذف فواتير')
    can_add_expense        = models.BooleanField(default=False, verbose_name='إضافة مصروفات')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'دور وظيفي'
        verbose_name_plural = 'الأدوار الوظيفية'
        unique_together = ['owner', 'name']
        ordering = ['-is_system', 'name']

    def __str__(self):
        return self.name

    def employee_count(self):
        return self.users.count()

    @staticmethod
    def create_defaults_for(owner):
        """ينشئ الأدوار الأساسية الثلاثة لصاحب عمل عند أول استخدام، إن لم تكن موجودة."""
        defaults = [
            dict(name='مدير', is_system=True, can_manage_users=True, can_delete_records=True,
                 can_view_reports=True, can_delete_customer=True, can_delete_product=True,
                 can_delete_sale=True, can_add_expense=True, can_manage_purchases=True),
            dict(name='كاشير', is_system=True, can_add_sale=True, can_add_customer=True,
                 can_edit_customer=True, can_add_product=True, can_edit_product=True,
                 can_view_all_customers=True),
            dict(name='مشاهد', is_system=True, can_view_reports=True, can_add_customer=False,
                 can_edit_customer=False, can_add_sale=False, can_add_product=False,
                 can_edit_product=False, can_view_all_customers=True),
        ]
        created = []
        for d in defaults:
            name = d.pop('name')
            role, was_created = Role.objects.get_or_create(owner=owner, name=name, defaults=d)
            created.append(role)
        return created


class User(AbstractUser):
    """Custom User model with owner hierarchy"""
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, null=True, blank=True,
        related_name='users', verbose_name='الدور الوظيفي',
        help_text='فارغ لصاحب الحساب الرئيسي فقط'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='employees', verbose_name='المالك الرئيسي'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='الهاتف')
    is_active = models.BooleanField(default=True, verbose_name='نشط')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'

    def get_owner(self):
        """Returns the root owner of this user"""
        if self.is_owner_account:
            return self
        return self.parent.get_owner()

    @property
    def is_owner_account(self):
        """صاحب الحساب الرئيسي: لا والد له ولا دور مُسنَد إليه"""
        return self.parent_id is None

    def can_manage_users(self):
        return self.is_owner_account or self.has_perm_flag('can_manage_users')

    def can_delete(self):
        return self.is_owner_account or self.has_perm_flag('can_delete_records')

    def has_perm_flag(self, code):
        """
        يتحقق من صلاحية محددة (مثل can_add_product) اعتماداً على دور الموظف.
        صاحب الحساب الرئيسي يملك كل الصلاحيات دائماً.
        """
        if self.is_owner_account:
            return True
        if not self.role_id:
            return False
        return getattr(self.role, code, False)

    @property
    def role_label(self):
        if self.is_owner_account:
            return 'مالك'
        return self.role.name if self.role_id else '—'

    @property
    def role_slug(self):
        """لتلوين شارة الدور في الواجهة"""
        if self.is_owner_account:
            return 'owner'
        if not self.role_id:
            return 'custom'
        mapping = {'مدير': 'manager', 'كاشير': 'cashier', 'مشاهد': 'viewer'}
        return mapping.get(self.role.name, 'custom')

    def __str__(self):
        return f'{self.get_full_name() or self.username} ({self.role_label})'
