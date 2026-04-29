"""URL routing for the reports app."""

from django.urls import path

from . import views


app_name = 'reports'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:report_key>/pdf/', views.download_pdf, name='download_pdf'),
    path('<str:report_key>/xlsx/', views.download_excel, name='download_excel'),
]
