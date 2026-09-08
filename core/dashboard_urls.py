from django.urls import path
from core import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('stats/api/', views.dashboard_stats_api, name='dashboard_stats_api'),
]
