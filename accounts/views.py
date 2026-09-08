from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Role
from .forms import LoginForm, UserCreateForm, UserEditForm, RoleForm


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request.POST or None)
    if form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )
        if user and user.is_active:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def user_list(request):
    if not request.user.can_manage_users():
        messages.error(request, 'ليس لديك صلاحية لإدارة المستخدمين')
        return redirect('dashboard')

    owner = request.user.get_owner()
    users = User.objects.filter(parent=owner).select_related('role').order_by('-created_at')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
def user_create(request):
    if not request.user.can_manage_users():
        messages.error(request, 'ليس لديك صلاحية')
        return redirect('dashboard')

    owner = request.user.get_owner()
    Role.create_defaults_for(owner)  # يضمن وجود الأدوار الأساسية قبل عرض النموذج
    form = UserCreateForm(request.POST or None, owner=owner)
    if form.is_valid():
        user = form.save(commit=False)
        user.parent = owner
        user.save()
        messages.success(request, f'تم إنشاء حساب {user.username} بنجاح')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'إضافة موظف جديد'})


@login_required
def user_edit(request, pk):
    if not request.user.can_manage_users():
        messages.error(request, 'ليس لديك صلاحية')
        return redirect('dashboard')

    owner = request.user.get_owner()
    user = get_object_or_404(User, pk=pk, parent=owner)
    form = UserEditForm(request.POST or None, instance=user, owner=owner)
    if form.is_valid():
        form.save()
        messages.success(request, 'تم تحديث بيانات المستخدم')
        return redirect('user_list')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': f'تعديل: {user.username}'})


@login_required
def user_delete(request, pk):
    if not request.user.is_owner_account:
        messages.error(request, 'هذه الصلاحية للمالك فقط')
        return redirect('user_list')
    user = get_object_or_404(User, pk=pk, parent=request.user.get_owner())
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'تم حذف المستخدم: {username}')
    return redirect('user_list')


@login_required
def profile(request):
    from .forms import ProfileForm
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, 'تم تحديث الملف الشخصي')
        return redirect('profile')
    return render(request, 'accounts/profile.html', {'form': form})


# ═══════════════════════════════════════
#  إدارة الأدوار الوظيفية والصلاحيات
# ═══════════════════════════════════════

@login_required
def role_list(request):
    if not request.user.is_owner_account:
        messages.error(request, 'إدارة الأدوار متاحة لصاحب الحساب الرئيسي فقط')
        return redirect('dashboard')
    owner = request.user.get_owner()
    Role.create_defaults_for(owner)
    roles = Role.objects.filter(owner=owner)
    return render(request, 'accounts/role_list.html', {'roles': roles})


@login_required
def role_create(request):
    if not request.user.is_owner_account:
        messages.error(request, 'إدارة الأدوار متاحة لصاحب الحساب الرئيسي فقط')
        return redirect('dashboard')
    owner = request.user.get_owner()
    form = RoleForm(request.POST or None)
    if form.is_valid():
        if Role.objects.filter(owner=owner, name__iexact=form.cleaned_data['name']).exists():
            form.add_error('name', 'يوجد دور بهذا الاسم مسبقاً')
        else:
            role = form.save(commit=False)
            role.owner = owner
            role.save()
            messages.success(request, f'تم إنشاء الدور: {role.name}')
            return redirect('role_list')
    return render(request, 'accounts/role_form.html', {'form': form, 'title': 'إضافة دور جديد'})


@login_required
def role_edit(request, pk):
    if not request.user.is_owner_account:
        messages.error(request, 'إدارة الأدوار متاحة لصاحب الحساب الرئيسي فقط')
        return redirect('dashboard')
    owner = request.user.get_owner()
    role = get_object_or_404(Role, pk=pk, owner=owner)
    form = RoleForm(request.POST or None, instance=role)
    if form.is_valid():
        dup = Role.objects.filter(owner=owner, name__iexact=form.cleaned_data['name']).exclude(pk=role.pk)
        if dup.exists():
            form.add_error('name', 'يوجد دور بهذا الاسم مسبقاً')
        else:
            form.save()
            messages.success(request, f'تم تحديث صلاحيات الدور: {role.name}')
            return redirect('role_list')
    return render(request, 'accounts/role_form.html', {
        'form': form, 'title': f'تعديل صلاحيات: {role.name}', 'role': role
    })


@login_required
def role_delete(request, pk):
    if not request.user.is_owner_account:
        messages.error(request, 'إدارة الأدوار متاحة لصاحب الحساب الرئيسي فقط')
        return redirect('dashboard')
    owner = request.user.get_owner()
    role = get_object_or_404(Role, pk=pk, owner=owner)
    if role.is_system:
        messages.error(request, 'لا يمكن حذف الأدوار الأساسية، يمكنك تعديل صلاحياتها فقط')
        return redirect('role_list')
    if role.employee_count() > 0:
        messages.error(request, f'لا يمكن حذف هذا الدور لوجود {role.employee_count()} موظف مُسند إليه، غيّر دورهم أولاً')
        return redirect('role_list')
    if request.method == 'POST':
        name = role.name
        role.delete()
        messages.success(request, f'تم حذف الدور: {name}')
    return redirect('role_list')
