from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_costing, name='daily_costing'),           # Now accessible at /costing/
    path('saved-costings/', views.saved_costings, name='saved_costings'),
    path('summary-report/', views.summary_report, name='summary_report'),
]