from django.urls import include, path
from .views import LoanList, create_loan,LoanDetail, LoanListByCustomer


urlpatterns = [
    path('create-loan/', create_loan, name='create-loan'),
    path('', LoanList.as_view()),
    path('view-loan/<int:pk>/', LoanDetail.as_view(), name='retrieve-loan'),
    path('view-loans/<int:customer_id>/', LoanListByCustomer.as_view(), name='retrieve-loan-by-customer'),
]
