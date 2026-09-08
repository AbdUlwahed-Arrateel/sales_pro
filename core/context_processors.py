from inventory.models import Product
from django.db.models import F


def global_context(request):
    context = {}
    if request.user.is_authenticated:
        owner = request.user.get_owner()
        low_stock_count = Product.objects.filter(
            owner=owner, 
            current_stock__lte=F('min_stock')
        ).count()
        context['low_stock_count'] = low_stock_count
        context['current_user'] = request.user
    return context
