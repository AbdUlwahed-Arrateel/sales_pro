from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F, Value, DecimalField, ExpressionWrapper
from django.db.models.functions import Coalesce
from .models import Customer
from .forms import CustomerForm
from sales.models import Invoice


def _with_balance(queryset):
    """يضيف لكل زبون إجمالي المشتريات والمدفوع والرصيد المستحق (مشتريات - مدفوع)."""
    money_field = DecimalField(max_digits=14, decimal_places=3)
    return queryset.annotate(
        total_purchases=Coalesce(Sum('invoices__total_amount'), Value(0), output_field=money_field),
        total_paid=Coalesce(Sum('invoices__paid_amount'), Value(0), output_field=money_field),
    ).annotate(
        balance=ExpressionWrapper(F('total_purchases') - F('total_paid'), output_field=money_field)
    )


@login_required
def customer_list(request):
    owner = request.user.get_owner()
    q = request.GET.get('q', '')
    activity = request.GET.get('activity', '')
    
    customers = Customer.objects.filter(owner=owner)
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(business_name__icontains=q) | Q(personal_phone__icontains=q))
    if activity:
        customers = customers.filter(activity_type=activity)
    
    customers = _with_balance(customers).order_by('name')

    paginator = Paginator(customers, 20)
    page = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'customers/list.html', {
        'page_obj': page, 'q': q, 'activity': activity,
        'total_count': customers.count()
    })


@login_required
def customer_create(request):
    if not request.user.has_perm_flag('can_add_customer'):
        messages.error(request, 'ليس لديك صلاحية إضافة زبون')
        return redirect('customer_list')
    form = CustomerForm(request.POST or None)
    if form.is_valid():
        customer = form.save(commit=False)
        customer.owner = request.user.get_owner()
        customer.save()
        messages.success(request, f'تم إضافة الزبون {customer.name} بنجاح')
        return redirect('customer_list')
    return render(request, 'customers/form.html', {'form': form, 'title': 'إضافة زبون جديد'})


@login_required
def customer_edit(request, pk):
    if not request.user.has_perm_flag('can_edit_customer'):
        messages.error(request, 'ليس لديك صلاحية تعديل بيانات الزبائن')
        return redirect('customer_list')
    customer = get_object_or_404(Customer, pk=pk, owner=request.user.get_owner())
    form = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid():
        form.save()
        messages.success(request, 'تم تحديث بيانات الزبون')
        return redirect('customer_detail', pk=pk)
    return render(request, 'customers/form.html', {'form': form, 'title': f'تعديل: {customer.name}'})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk, owner=request.user.get_owner())
    invoices = Invoice.objects.filter(customer=customer).order_by('-created_at')
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        invoices = invoices.filter(created_at__date__gte=date_from)
    if date_to:
        invoices = invoices.filter(created_at__date__lte=date_to)
    
    totals = invoices.aggregate(total=Sum('total_amount'), paid=Sum('paid_amount'))
    balance = (totals['total'] or 0) - (totals['paid'] or 0)
    
    paginator = Paginator(invoices, 15)
    page = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'customers/detail.html', {
        'customer': customer,
        'page_obj': page,
        'total_amount': totals['total'] or 0,
        'total_paid': totals['paid'] or 0,
        'balance': balance,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def customer_delete(request, pk):
    if not (request.user.can_delete() or request.user.has_perm_flag('can_delete_customer')):
        messages.error(request, 'ليس لديك صلاحية الحذف')
        return redirect('customer_list')
    customer = get_object_or_404(Customer, pk=pk, owner=request.user.get_owner())
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f'تم حذف الزبون {name}')
    return redirect('customer_list')


@login_required
def all_customers_statement(request):
    """كشف جميع الزبائن"""
    owner = request.user.get_owner()
    customers = _with_balance(Customer.objects.filter(owner=owner)).order_by('name')

    total_sales = sum(c.total_purchases for c in customers)
    total_paid = sum(c.total_paid for c in customers)
    total_balance = total_sales - total_paid
    
    return render(request, 'customers/all_statement.html', {
        'customers': customers,
        'total_sales': total_sales,
        'total_paid': total_paid,
        'total_balance': total_balance,
    })
