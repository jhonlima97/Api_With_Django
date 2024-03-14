from django.urls import path
from .views import CompanyView

urlpatterns=[
    path('v1/companies/', CompanyView.as_view(), name='companies_list'),
    path('v1/companies/<int:id>', CompanyView.as_view(), name='companies_process')
]