from django.urls import path
from . import views

urlpatterns = [
    path('', views.GetCountrySummaryView.as_view())
    ]
