from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.project_list, name='list'),
    path('create/', views.project_create, name='create'),
    path('<int:pk>/', views.project_detail, name='detail'),
    path('<int:pk>/edit/', views.project_edit, name='edit'),
    path('<int:pk>/delete/', views.project_delete, name='delete'),

    # Sprint URLs
    path('<int:project_pk>/sprints/create/', views.sprint_create, name='sprint_create'),
    path('<int:project_pk>/sprints/<int:pk>/edit/', views.sprint_edit, name='sprint_edit'),
    path('<int:project_pk>/sprints/<int:pk>/delete/', views.sprint_delete, name='sprint_delete'),
]