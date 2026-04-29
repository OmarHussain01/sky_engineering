from django.urls import path

from . import views


urlpatterns = [
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('relationships/', views.org_relationships, name='org_relationships'),
]
