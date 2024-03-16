from django.urls import path

from . import views

urlpatterns = [
    path('daily_stats/', views.daily_stats, name='daily_stats'),
    path('tasks_stats/', views.tasks_stats, name='tasks_stats')
]
