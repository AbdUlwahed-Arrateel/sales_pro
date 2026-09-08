from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def pos_view(request):
    initial_customer = None
    customer_id = request.GET.get('customer')
    if customer_id:
        from customers.models import Customer
        owner = request.user.get_owner()
        customer = Customer.objects.filter(pk=customer_id, owner=owner).first()
        if customer:
            initial_customer = {'id': customer.id, 'name': customer.name}
    return render(request, 'pos/index.html', {'initial_customer': initial_customer})
