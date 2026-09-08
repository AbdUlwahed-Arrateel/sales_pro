from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, F
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Product, Purchase, Supplier, Category
from .forms import ProductForm, ProductPricingForm, PurchaseForm, SupplierForm, CategoryForm


# ═══════════════════════════════════════
#  الأصناف
# ═══════════════════════════════════════

@login_required
def product_list(request):
    owner = request.user.get_owner()
    q         = request.GET.get('q', '')
    category  = request.GET.get('category', '')
    low_stock = request.GET.get('low_stock', '')

    products = Product.objects.filter(owner=owner, is_active=True)
    if q:         products = products.filter(Q(name__icontains=q) | Q(barcode__icontains=q))
    if category:  products = products.filter(category_id=category)
    if low_stock: products = products.filter(current_stock__lte=F('min_stock'))

    categories = Category.objects.filter(owner=owner)
    paginator  = Paginator(products, 20)
    page       = paginator.get_page(request.GET.get('page'))

    return render(request, 'inventory/product_list.html', {
        'page_obj': page, 'q': q, 'categories': categories,
        'selected_category': category,
    })


@login_required
def product_create(request):
    if not request.user.has_perm_flag('can_add_product'):
        messages.error(request, 'ليس لديك صلاحية إضافة صنف')
        return redirect('product_list')
    owner = request.user.get_owner()
    form  = ProductForm(request.POST or None, owner=owner)
    if form.is_valid():
        product = form.save(commit=False)
        product.owner = owner
        product.save()
        messages.success(request, f'تم إضافة الصنف: {product.name}')
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {'form': form, 'title': 'إضافة صنف جديد'})


@login_required
def product_edit(request, pk):
    if not request.user.has_perm_flag('can_edit_product'):
        messages.error(request, 'ليس لديك صلاحية تعديل الأصناف')
        return redirect('product_list')
    owner   = request.user.get_owner()
    product = get_object_or_404(Product, pk=pk, owner=owner)
    form    = ProductForm(request.POST or None, instance=product, owner=owner)
    if form.is_valid():
        form.save()
        messages.success(request, 'تم تحديث الصنف')
        return redirect('product_list')
    return render(request, 'inventory/product_form.html', {
        'form': form, 'title': f'تعديل: {product.name}', 'product': product
    })


@login_required
def product_pricing(request, pk):
    if not request.user.has_perm_flag('can_edit_product'):
        messages.error(request, 'ليس لديك صلاحية تعديل الأسعار')
        return redirect('product_list')
    owner   = request.user.get_owner()
    product = get_object_or_404(Product, pk=pk, owner=owner)
    form    = ProductPricingForm(request.POST or None, instance=product)
    if form.is_valid():
        form.save()
        messages.success(request, f'تم تحديث أسعار {product.name}')
        return redirect('product_list')
    return render(request, 'inventory/product_pricing.html', {
        'form': form, 'product': product, 'title': f'تعديل أسعار: {product.name}'
    })


@login_required
def product_delete(request, pk):
    if not (request.user.can_delete() or request.user.has_perm_flag('can_delete_product')):
        messages.error(request, 'ليس لديك صلاحية الحذف')
        return redirect('product_list')
    product = get_object_or_404(Product, pk=pk, owner=request.user.get_owner())
    if request.method == 'POST':
        product.is_active = False
        product.save()
        messages.success(request, f'تم حذف الصنف: {product.name}')
    return redirect('product_list')


@login_required
@require_POST
def category_create_api(request):
    """إضافة فئة جديدة سريعاً من نموذج الصنف (AJAX)"""
    if not request.user.has_perm_flag('can_add_product'):
        return JsonResponse({'error': 'ليس لديك صلاحية إضافة فئة'}, status=403)
    owner = request.user.get_owner()
    name = request.POST.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'اسم الفئة مطلوب'}, status=400)
    if Category.objects.filter(owner=owner, name__iexact=name).exists():
        return JsonResponse({'error': 'هذه الفئة موجودة مسبقاً'}, status=400)
    category = Category.objects.create(owner=owner, name=name)
    return JsonResponse({'id': category.id, 'name': category.name})


# ═══════════════════════════════════════
#  المشتريات
# ═══════════════════════════════════════

@login_required
def purchase_list(request):
    owner     = request.user.get_owner()
    purchases = Purchase.objects.filter(owner=owner).select_related('product', 'supplier')

    date_from  = request.GET.get('date_from', '')
    date_to    = request.GET.get('date_to', '')
    product_id = request.GET.get('product', '')

    if date_from:   purchases = purchases.filter(purchase_date__gte=date_from)
    if date_to:     purchases = purchases.filter(purchase_date__lte=date_to)
    if product_id:  purchases = purchases.filter(product_id=product_id)

    total_cost = purchases.aggregate(t=Sum('total_cost'))['t'] or 0
    products   = Product.objects.filter(owner=owner, is_active=True)
    paginator  = Paginator(purchases, 20)
    page       = paginator.get_page(request.GET.get('page'))

    return render(request, 'inventory/purchase_list.html', {
        'page_obj': page, 'total_cost': total_cost,
        'products': products, 'date_from': date_from, 'date_to': date_to,
    })


@login_required
def purchase_create(request):
    if not request.user.has_perm_flag('can_manage_purchases'):
        messages.error(request, 'ليس لديك صلاحية تسجيل المشتريات')
        return redirect('purchase_list')
    owner = request.user.get_owner()
    initial = {}
    product_id = request.GET.get('product')
    if product_id:
        initial['product'] = product_id
    form = PurchaseForm(request.POST or None, owner=owner, initial=initial)
    if form.is_valid():
        purchase = form.save(commit=False)
        purchase.owner = owner
        purchase.save()

        # تحديث سعر البيع (قطاعي/جملة) للصنف إن تم تحديده أثناء الشراء
        product = purchase.product
        new_retail    = form.cleaned_data.get('new_retail_price')
        new_wholesale = form.cleaned_data.get('new_wholesale_price')
        if new_retail is not None:
            product.retail_price = new_retail
        if new_wholesale is not None:
            product.wholesale_price = new_wholesale
        if new_retail is not None or new_wholesale is not None:
            product.save()

        messages.success(request, f'تم تسجيل: {purchase.product.name} × {purchase.quantity}')
        return redirect('purchase_list')

    products = Product.objects.filter(owner=owner, is_active=True).values(
        'id', 'retail_price', 'wholesale_price'
    )
    return render(request, 'inventory/purchase_form.html', {
        'form': form, 'title': 'تسجيل مشتريات', 'products_json': list(products),
    })


# ═══════════════════════════════════════
#  الموردون
# ═══════════════════════════════════════

@login_required
def supplier_list(request):
    owner     = request.user.get_owner()
    suppliers = Supplier.objects.filter(owner=owner)
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})


@login_required
def supplier_create(request):
    if not request.user.has_perm_flag('can_manage_purchases'):
        messages.error(request, 'ليس لديك صلاحية إدارة الموردين')
        return redirect('supplier_list')
    form = SupplierForm(request.POST or None)
    if form.is_valid():
        supplier = form.save(commit=False)
        supplier.owner = request.user.get_owner()
        supplier.save()
        messages.success(request, 'تم إضافة المورد')
        return redirect('supplier_list')
    return render(request, 'inventory/supplier_form.html', {'form': form, 'title': 'إضافة مورد'})


@login_required
def supplier_edit(request, pk):
    if not request.user.has_perm_flag('can_manage_purchases'):
        messages.error(request, 'ليس لديك صلاحية تعديل الموردين')
        return redirect('supplier_list')
    supplier = get_object_or_404(Supplier, pk=pk, owner=request.user.get_owner())
    form = SupplierForm(request.POST or None, instance=supplier)
    if form.is_valid():
        form.save()
        messages.success(request, 'تم تحديث بيانات المورد')
        return redirect('supplier_list')
    return render(request, 'inventory/supplier_form.html', {
        'form': form, 'title': f'تعديل مورد: {supplier.name}'
    })


@login_required
def supplier_delete(request, pk):
    if not (request.user.can_delete() or request.user.has_perm_flag('can_manage_purchases')):
        messages.error(request, 'ليس لديك صلاحية الحذف')
        return redirect('supplier_list')
    supplier = get_object_or_404(Supplier, pk=pk, owner=request.user.get_owner())
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        messages.success(request, f'تم حذف المورد: {name}')
    return redirect('supplier_list')


# ═══════════════════════════════════════
#  الجرد
# ═══════════════════════════════════════

@login_required
def inventory_report(request):
    if not request.user.has_perm_flag('can_view_reports'):
        messages.error(request, 'ليس لديك صلاحية عرض التقارير')
        return redirect('product_list')
    owner    = request.user.get_owner()
    products = Product.objects.filter(owner=owner, is_active=True).select_related('category')

    products_data        = []
    total_retail_value   = 0
    total_wholesale_value = 0
    total_cost_value     = 0

    for p in products:
        stock = float(p.current_stock)

        rv = stock * float(p.retail_price)
        wv = stock * float(p.wholesale_price)
        cv = stock * float(p.cost_price)
        products_data.append({'product': p, 'stock': stock, 'retail_value': rv, 'wholesale_value': wv, 'cost_value': cv})
        total_retail_value   += rv
        total_wholesale_value += wv
        total_cost_value     += cv

    return render(request, 'inventory/inventory_report.html', {
        'products_data': products_data,
        'total_retail_value':    total_retail_value,
        'total_wholesale_value': total_wholesale_value,
        'total_cost_value':      total_cost_value,
    })
