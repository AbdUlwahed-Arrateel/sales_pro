from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta, date


@login_required
def reports_home(request):
    if not request.user.has_perm_flag('can_view_reports'):
        messages.error(request, 'ليس لديك صلاحية عرض التقارير')
        return redirect('dashboard')
    return render(request, 'reports/home.html')


@login_required
def profit_loss_report(request):
    if not request.user.has_perm_flag('can_view_reports'):
        messages.error(request, 'ليس لديك صلاحية عرض التقارير')
        return redirect('dashboard')
    from sales.models import Invoice
    from expenses.models import Expense
    
    owner = request.user.get_owner()
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    
    if period == 'today':
        start = today
        end = today
    elif period == 'week':
        start = today - timedelta(days=6)
        end = today
    elif period == 'month':
        start = today.replace(day=1)
        end = today
    elif period == 'year':
        start = today.replace(month=1, day=1)
        end = today
    else:
        start = date.fromisoformat(request.GET.get('date_from', str(today.replace(day=1))))
        end = date.fromisoformat(request.GET.get('date_to', str(today)))
    
    invoices = Invoice.objects.filter(owner=owner, created_at__date__gte=start, created_at__date__lte=end)
    expenses = Expense.objects.filter(owner=owner, date__gte=start, date__lte=end)
    
    total_sales = invoices.aggregate(t=Sum('total_amount'))['t'] or 0
    total_paid = invoices.aggregate(t=Sum('paid_amount'))['t'] or 0
    total_expenses = expenses.aggregate(t=Sum('amount'))['t'] or 0
    net_profit = total_sales - total_expenses
    
    retail_sales = invoices.filter(sale_type='retail').aggregate(t=Sum('total_amount'))['t'] or 0
    wholesale_sales = invoices.filter(sale_type='wholesale').aggregate(t=Sum('total_amount'))['t'] or 0
    
    return render(request, 'reports/profit_loss.html', {
        'total_sales': total_sales,
        'total_paid': total_paid,
        'total_balance': total_sales - total_paid,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'retail_sales': retail_sales,
        'wholesale_sales': wholesale_sales,
        'invoice_count': invoices.count(),
        'period': period,
        'start': start,
        'end': end,
        'expenses_by_category': expenses.values('category__name').annotate(total=Sum('amount')).order_by('-total'),
    })
