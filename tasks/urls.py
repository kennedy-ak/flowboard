from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('create/', views.task_create, name='create'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('<int:pk>/edit/', views.task_edit, name='edit'),
    path('<int:pk>/delete/', views.task_delete, name='delete'),
    path('<int:pk>/status/', views.task_update_status, name='update_status'),

    # Subtask URLs
    path('<int:task_pk>/subtasks/create/', views.subtask_create, name='subtask_create'),
    path('<int:task_pk>/subtasks/<int:pk>/edit/', views.subtask_edit, name='subtask_edit'),
    path('<int:task_pk>/subtasks/<int:pk>/delete/', views.subtask_delete, name='subtask_delete'),
    path('<int:task_pk>/subtasks/<int:pk>/status/', views.subtask_update_status, name='subtask_update_status'),

    # Comment URLs
    path('<int:task_pk>/comments/add/', views.comment_add, name='comment_add'),
    path('<int:task_pk>/subtasks/<int:subtask_pk>/comments/add/', views.subtask_comment_add, name='subtask_comment_add'),
]