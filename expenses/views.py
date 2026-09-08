from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Expense, ExpenseCategory
from .forms import ExpenseForm, ExpenseCategoryForm


@login_required
def expense_list(request):
    if not request.user.has_perm_flag('can_view_reports'):
        messages.error(request, 'ليس لديك صلاحية عرض المصروفات')
        return redirect('dashboard')
    owner = request.user.get_owner()
    expenses = Expense.objects.filter(owner=owner).select_related('category', 'created_by')
    
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    category_id = request.GET.get('category', '')
    
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)
    if category_id:
        expenses = expenses.filter(category_id=category_id)
    
    total = expenses.aggregate(t=Sum('amount'))['t'] or 0
    categories = ExpenseCategory.objects.filter(owner=owner)
    
    paginator = Paginator(expenses, 20)
    page = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'expenses/list.html', {
        'page_obj': page, 'total': total, 'categories': categories,
        'date_from': date_from, 'date_to': date_to, 'selected_category': category_id,
    })


@login_required
def expense_create(request):
    if not request.user.has_perm_flag('can_add_expense'):
        messages.error(request, 'ليس لديك صلاحية إضافة مصروف')
        return redirect('expense_list')
    owner = request.user.get_owner()
    form = ExpenseForm(request.POST or None, owner=owner)
    if form.is_valid():
        expense = form.save(commit=False)
        expense.owner = owner
        expense.created_by = request.user
        expense.save()
        messages.success(request, f'تم تسجيل المصروف: {expense.description}')
        return redirect('expense_list')
    return render(request, 'expenses/form.html', {'form': form, 'title': 'تسجيل مصروف'})


@login_required
def expense_delete(request, pk):
    if not request.user.can_delete():
        messages.error(request, 'ليس لديك صلاحية')
        return redirect('expense_list')
    expense = get_object_or_404(Expense, pk=pk, owner=request.user.get_owner())
    if request.method == 'POST':
        expense.delete()
        messages.success(request, 'تم حذف المصروف')
    return redirect('expense_list')


@login_required
@require_POST
def expense_category_create_api(request):
    """إضافة فئة مصروف جديدة سريعاً من نموذج تسجيل المصروف (AJAX)"""
    if not request.user.has_perm_flag('can_add_expense'):
        return JsonResponse({'error': 'ليس لديك صلاحية إضافة فئة'}, status=403)
    owner = request.user.get_owner()
    name = request.POST.get('name', '').strip()
    icon = request.POST.get('icon', '💰').strip() or '💰'
    if not name:
        return JsonResponse({'error': 'اسم الفئة مطلوب'}, status=400)
    if ExpenseCategory.objects.filter(owner=owner, name__iexact=name).exists():
        return JsonResponse({'error': 'هذه الفئة موجودة مسبقاً'}, status=400)
    category = ExpenseCategory.objects.create(owner=owner, name=name, icon=icon)
    return JsonResponse({'id': category.id, 'name': category.name})
