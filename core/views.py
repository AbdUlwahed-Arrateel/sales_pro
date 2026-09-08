from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import timedelta, date
import json

from sales.models import Invoice, SaleItem
from customers.models import Customer
from inventory.models import Product, Purchase
from expenses.models import Expense


def _calc_profit(owner, date_from, date_to):
    """
    الربح الحقيقي = مجموع (سعر البيع - سعر التكلفة) × الكمية لكل بند مباع
                   مطروحاً منه المصروفات في نفس الفترة.
    """
    items = SaleItem.objects.filter(
        invoice__owner=owner,
        invoice__created_at__date__gte=date_from,
        invoice__created_at__date__lte=date_to,
    ).select_related('product')

    gross_profit = sum(
        float(item.quantity) * (float(item.unit_price) - float(item.product.cost_price))
        for item in items
    )

    expenses = Expense.objects.filter(
        owner=owner, date__gte=date_from, date__lte=date_to
    ).aggregate(t=Sum('amount'))['t'] or 0

    return gross_profit, float(expenses), gross_profit - float(expenses)


@login_required
def dashboard(request):
    today = timezone.now().date()
    owner = request.user.get_owner()

    # ── إحصائيات اليوم ──────────────────────────────────────
    today_invoices = Invoice.objects.filter(created_at__date=today, owner=owner)
    today_sales    = today_invoices.aggregate(t=Sum('total_amount'))['t'] or 0
    today_paid     = today_invoices.aggregate(t=Sum('paid_amount'))['t'] or 0
    today_expenses = Expense.objects.filter(date=today, owner=owner).aggregate(t=Sum('amount'))['t'] or 0

    today_gross, _, today_net = _calc_profit(owner, today, today)

    # ── إحصائيات الشهر ──────────────────────────────────────
    month_start = today.replace(day=1)
    month_invoices = Invoice.objects.filter(created_at__date__gte=month_start, owner=owner)
    month_sales    = month_invoices.aggregate(t=Sum('total_amount'))['t'] or 0
    month_expenses = Expense.objects.filter(date__gte=month_start, owner=owner).aggregate(t=Sum('amount'))['t'] or 0
    month_gross, _, month_net = _calc_profit(owner, month_start, today)

    # ── إجماليات عامة ───────────────────────────────────────
    total_customers = Customer.objects.filter(owner=owner).count()
    low_stock       = Product.objects.filter(owner=owner, current_stock__lte=F('min_stock')).count()

    # ── آخر الفواتير ─────────────────────────────────────────
    recent_invoices = Invoice.objects.filter(owner=owner).select_related('customer').order_by('-created_at')[:10]

    # ── أفضل الزبائن هذا الشهر ──────────────────────────────
    top_customers = Customer.objects.filter(
        owner=owner,
        invoices__created_at__date__gte=month_start
    ).annotate(month_total=Sum('invoices__total_amount')).order_by('-month_total')[:5]

    # ── بيانات الرسم البياني (7 أيام) ───────────────────────
    chart_labels   = []
    chart_sales    = []
    chart_expenses = []
    chart_profit   = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        chart_labels.append(d.strftime('%d/%m'))
        ds  = Invoice.objects.filter(created_at__date=d, owner=owner).aggregate(t=Sum('total_amount'))['t'] or 0
        de  = Expense.objects.filter(date=d, owner=owner).aggregate(t=Sum('amount'))['t'] or 0
        _, _, dp = _calc_profit(owner, d, d)
        chart_sales.append(float(ds))
        chart_expenses.append(float(de))
        chart_profit.append(float(dp))

    context = {
        'today_sales':    today_sales,
        'today_paid':     today_paid,
        'today_expenses': today_expenses,
        'today_gross':    today_gross,
        'today_net':      today_net,
        'month_sales':    month_sales,
        'month_expenses': month_expenses,
        'month_gross':    month_gross,
        'month_net':      month_net,
        'total_customers': total_customers,
        'low_stock':      low_stock,
        'recent_invoices': recent_invoices,
        'top_customers':  top_customers,
        'invoice_count_today': today_invoices.count(),
        'chart_labels':   json.dumps(chart_labels),
        'chart_sales':    json.dumps(chart_sales),
        'chart_expenses': json.dumps(chart_expenses),
        'chart_profit':   json.dumps(chart_profit),
        'month_net_json':      json.dumps(float(month_net)),
        'month_expenses_json': json.dumps(float(month_expenses)),
        'month_sales_json':    json.dumps(float(month_sales)),
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def dashboard_stats_api(request):
    period = request.GET.get('period', 'week')
    today  = timezone.now().date()
    owner  = request.user.get_owner()

    if period == 'week':
        dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
        labels = [d.strftime('%d/%m') for d in dates]
    elif period == 'month':
        dates = [today - timedelta(days=i) for i in range(29, -1, -1)]
        labels = [d.strftime('%d/%m') for d in dates]
    elif period == 'year':
        dates  = [date(today.year, m, 1) for m in range(1, 13)]
        labels = [f'{m}/{today.year}' for m in range(1, 13)]
    else:  # today
        dates  = [today]
        labels = [today.strftime('%d/%m')]

    sales_data = []
    exp_data   = []
    profit_data = []

    for d in dates:
        if period == 'year':
            s = Invoice.objects.filter(owner=owner, created_at__year=d.year, created_at__month=d.month).aggregate(t=Sum('total_amount'))['t'] or 0
            e = Expense.objects.filter(owner=owner, date__year=d.year, date__month=d.month).aggregate(t=Sum('amount'))['t'] or 0
            d_start = d
            d_end   = date(d.year, d.month, 28)  # تقريب
        else:
            s = Invoice.objects.filter(owner=owner, created_at__date=d).aggregate(t=Sum('total_amount'))['t'] or 0
            e = Expense.objects.filter(owner=owner, date=d).aggregate(t=Sum('amount'))['t'] or 0
            d_start = d_end = d

        _, _, profit = _calc_profit(owner, d_start, d_end)
        sales_data.append(float(s))
        exp_data.append(float(e))
        profit_data.append(float(profit))

    return JsonResponse({
        'labels':   labels,
        'sales':    sales_data,
        'expenses': exp_data,
        'profit':   profit_data,
    })
