from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('profit-loss/', views.profit_loss_report, name='profit_loss_report'),
]
