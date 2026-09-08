import json
import logging
from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST

from .models import Invoice, SaleItem, Payment
from customers.models import Customer
from inventory.models import Product

logger = logging.getLogger(__name__)


@login_required
def invoice_list(request):
    owner    = request.user.get_owner()
    invoices = Invoice.objects.filter(owner=owner).select_related('customer', 'created_by')

    q         = request.GET.get('q', '')
    status    = request.GET.get('status', '')
    sale_type = request.GET.get('sale_type', '')
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')

    if q:         invoices = invoices.filter(Q(customer__name__icontains=q) | Q(pk__icontains=q))
    if status:    invoices = invoices.filter(status=status)
    if sale_type: invoices = invoices.filter(sale_type=sale_type)
    if date_from: invoices = invoices.filter(created_at__date__gte=date_from)
    if date_to:   invoices = invoices.filter(created_at__date__lte=date_to)

    totals = invoices.aggregate(total=Sum('total_amount'), paid=Sum('paid_amount'))
    paginator = Paginator(invoices, 20)
    page = paginator.get_page(request.GET.get('page'))

    return render(request, 'sales/invoice_list.html', {
        'page_obj': page,
        'total_amount': totals['total'] or 0,
        'total_paid':   totals['paid']  or 0,
        'q': q, 'status': status, 'sale_type': sale_type,
        'date_from': date_from, 'date_to': date_to,
    })


@login_required
def invoice_detail(request, pk):
    invoice  = get_object_or_404(Invoice, pk=pk, owner=request.user.get_owner())
    items    = invoice.items.select_related('product')
    payments = invoice.payments.all()
    return render(request, 'sales/invoice_detail.html', {
        'invoice': invoice, 'items': items, 'payments': payments,
    })


@login_required
@require_POST
def add_payment(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user.get_owner())
    try:
        amount = float(request.POST.get('amount', 0))
        if amount <= 0:
            messages.error(request, 'مبلغ غير صحيح')
        else:
            Payment.objects.create(invoice=invoice, amount=amount,
                                   notes=request.POST.get('notes', ''),
                                   received_by=request.user)
            messages.success(request, f'تم تسجيل دفعة {amount:.3f}')
    except (ValueError, TypeError):
        messages.error(request, 'مبلغ غير صحيح')
    return redirect('invoice_detail', pk=pk)


@login_required
def invoice_delete(request, pk):
    if not (request.user.can_delete() or request.user.has_perm_flag('can_delete_sale')):
        messages.error(request, 'ليس لديك صلاحية الحذف')
        return redirect('invoice_list')
    invoice = get_object_or_404(Invoice, pk=pk, owner=request.user.get_owner())
    if request.method == 'POST':
        with transaction.atomic():
            for item in invoice.items.select_related('product'):
                item.product.current_stock += item.quantity
                item.product.save()
            invoice.delete()
        messages.success(request, 'تم حذف الفاتورة')
    return redirect('invoice_list')


# ── API للـ POS ────────────────────────────────────────────────────
@login_required
def api_products(request):
    owner = request.user.get_owner()
    q     = request.GET.get('q', '')
    prods = Product.objects.filter(owner=owner, is_active=True)
    if q:
        prods = prods.filter(Q(name__icontains=q) | Q(barcode__icontains=q))
    data = [{
        'id': p.id, 'name': p.name, 'barcode': p.barcode,
        'retail_price':    float(p.retail_price),
        'wholesale_price': float(p.wholesale_price),
        'stock':      float(p.current_stock),
        'unit':       p.get_unit_display(),
    } for p in prods[:60]]
    return JsonResponse({'products': data})


@login_required
def api_customers(request):
    owner = request.user.get_owner()
    q     = request.GET.get('q', '')
    cid   = request.GET.get('id', '')
    custs = Customer.objects.filter(owner=owner)
    if cid:
        custs = custs.filter(pk=cid)
    elif q:
        custs = custs.filter(Q(name__icontains=q) | Q(personal_phone__icontains=q))
    data = [{'id': c.id, 'name': c.name, 'phone': c.personal_phone,
              'balance': float(c.get_balance())} for c in custs[:20]]
    return JsonResponse({'customers': data})


@login_required
@require_POST
def create_invoice_api(request):
    """إنشاء فاتورة من POS"""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'بيانات الطلب غير صالحة'}, status=400)

    owner      = request.user.get_owner()
    if not request.user.has_perm_flag('can_add_sale'):
        return JsonResponse({'error': 'ليس لديك صلاحية إنشاء فاتورة'}, status=403)

    items_data = data.get('items', [])
    if not items_data:
        return JsonResponse({'error': 'الفاتورة فارغة'}, status=400)

    try:
        discount    = Decimal(str(data.get('discount', 0)))
        paid_amount = Decimal(str(data.get('paid_amount', 0)))
    except (TypeError, ValueError, InvalidOperation):
        return JsonResponse({'error': 'قيم الخصم أو المدفوع غير صحيحة'}, status=400)

    if discount < 0 or paid_amount < 0:
        return JsonResponse({'error': 'لا يمكن أن تكون القيم سالبة'}, status=400)

    sale_type = data.get('sale_type', 'retail')
    if sale_type not in dict(Invoice.SALE_TYPE_CHOICES):
        return JsonResponse({'error': 'نوع بيع غير صحيح'}, status=400)

    try:
        customer = None
        if data.get('customer_id'):
            customer = get_object_or_404(Customer, pk=data['customer_id'], owner=owner)

        # ── التحقق من صحة البنود والمخزون قبل أي تعديل ────────────
        parsed_items = []
        for item_data in items_data:
            product = get_object_or_404(Product, pk=item_data.get('product_id'), owner=owner)
            try:
                qty   = Decimal(str(item_data['quantity']))
                price = Decimal(str(item_data['price']))
            except (KeyError, TypeError, ValueError, InvalidOperation):
                return JsonResponse({'error': f'بيانات بند غير صحيحة للصنف {product.name}'}, status=400)

            if qty <= 0:
                return JsonResponse({'error': f'الكمية يجب أن تكون أكبر من صفر ({product.name})'}, status=400)
            if price < 0:
                return JsonResponse({'error': f'السعر غير صحيح ({product.name})'}, status=400)
            if qty > product.current_stock:
                return JsonResponse({
                    'error': f'الكمية المطلوبة من "{product.name}" أكبر من المخزون المتاح ({product.current_stock})'
                }, status=400)

            parsed_items.append({'product': product, 'quantity': qty, 'price': price})
    except Http404:
        return JsonResponse({'error': 'الزبون أو الصنف المطلوب غير موجود'}, status=404)

    total = sum((i['quantity'] * i['price'] for i in parsed_items), Decimal('0')) - discount
    total = max(Decimal('0'), total)

    try:
        with transaction.atomic():
            invoice = Invoice.objects.create(
                owner=owner, customer=customer, sale_type=sale_type,
                total_amount=total, discount=discount, paid_amount=0,
                notes=data.get('notes', ''), created_by=request.user,
            )

            for item in parsed_items:
                SaleItem.objects.create(
                    invoice=invoice, product=item['product'],
                    quantity=item['quantity'], unit_price=item['price'],
                )

            if paid_amount > 0:
                Payment.objects.create(invoice=invoice, amount=paid_amount, received_by=request.user)

        return JsonResponse({'success': True, 'invoice_id': invoice.pk})

    except Exception:
        logger.exception('Failed to create invoice for owner=%s', owner.pk)
        return JsonResponse({'error': 'حدث خطأ غير متوقع أثناء إنشاء الفاتورة، حاول مرة أخرى'}, status=500)
