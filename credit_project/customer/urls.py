from django.urls import include, path
from .views import CustomerCreate, CustomerList, CustomerDetail, CustomerUpdate, CustomerDelete,check_loan_eligibility


urlpatterns = [
    path('register/', CustomerCreate.as_view(), name='create-customer'),
    path('check-eligibility/', check_loan_eligibility, name='create-customer'),
    path('customers/', CustomerList.as_view()),
    # path('<int:pk>/', CustomerDetail.as_view(), name='retrieve-customer'),
    # path('update/<int:pk>/', CustomerUpdate.as_view(), name='update-customer'),
    path('delete/<int:pk>/', CustomerDelete.as_view(), name='delete-customer')
]
