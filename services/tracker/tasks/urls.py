from django.urls import path

from . import views

urlpatterns = [
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/<int:task_id>/close', views.task_close, name='close_task'),
    path('tasks/my', views.tasks_my, name='tasks_my'),
    path('tasks/shuffle', views.tasks_shuffle, name='tasks_shuffle')
]
