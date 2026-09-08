from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('create/', views.expense_create, name='expense_create'),
    path('<int:pk>/delete/', views.expense_delete, name='expense_delete'),
    path('api/categories/create/', views.expense_category_create_api, name='expense_category_create_api'),
]
