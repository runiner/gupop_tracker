from django.urls import path

from . import views

urlpatterns = [
    path('bills/my', views.bills_my, name='bills_my'),
    path('bills/', views.bills, name='bills'),
    path('close_period/', views.close_period, name='close_period'),
]
