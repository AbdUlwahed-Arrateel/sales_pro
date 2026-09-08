from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/payment/', views.add_payment, name='add_payment'),
    path('<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('api/products/', views.api_products, name='api_products'),
    path('api/customers/', views.api_customers, name='api_customers'),
    path('api/create/', views.create_invoice_api, name='create_invoice_api'),
]
