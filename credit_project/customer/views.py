from datetime import date
from dateutil import relativedelta
from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import Customer
from loans.models import Loan
from rest_framework import generics, status
from rest_framework.response import Response
from .serializers import CustomerSerializer
import pandas as pd

def ingest_excel_data(file_path):
    try:
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            customer = Customer(
                customer_id = row['Customer ID'],
                first_name=row['First Name'],
                last_name=row['Last Name'],
                phone_number=row['Phone Number'],
                age=row['Age'],
                monthly_salary=row['Monthly Salary'],
                approved_limit=row['Approved Limit'],
                current_debt = 0
            )
            customer.save()
    except Exception as e:
        print(f"Error ingesting Excel data: {e}")
    
class CustomerCreate(generics.CreateAPIView):
    # API endpoint that allows creation of a new customer
    queryset = Customer.objects.all(),
    serializer_class = CustomerSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            customer_instance = serializer.instance
            response_data = {
                'customer_id': customer_instance.customer_id,
                'name': customer_instance.full_name,
                'age': customer_instance.age,
                'monthly_income': customer_instance.monthly_salary,
                'approved_limit': customer_instance.approved_limit,
                'phone_number': customer_instance.phone_number
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerList(generics.ListAPIView):
    # API endpoint that allows customer to be viewed.
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class CustomerDetail(generics.RetrieveAPIView):
    # API endpoint that returns a single customer by pk.
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
class CustomerUpdate(generics.RetrieveUpdateAPIView):
    # API endpoint that allows a customer record to be updated.
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    
class CustomerDelete(generics.RetrieveDestroyAPIView):
    # API endpoint that allows a customer record to be deleted.
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

def calculate_loan_eligibility(customer,non_active_loans,active_loans,request_amount,interest_rate,tenure):
    credit_score = 100
    total_loan_amount = sum(loan.loan_amount for loan in active_loans)
    total_emi = sum(loan.monthly_repayment for loan in active_loans)
    if total_emi*2 >= customer.monthly_salary or total_loan_amount + request_amount >= customer.approved_limit:
        credit_score = 0
        
    # for active loans
    total_months = 0
    total_emis_on_time = sum(loan.emis_paid_on_time for loan in active_loans)
    for loan in active_loans:
        total_months  += relativedelta.relativedelta(loan.end_date, loan.start_date).months
    
    if total_emis_on_time < 0.8 * total_months:
        credit_score -= 10
    
    # for old (non active) loans
    total_emis_on_time = sum(loan.emis_paid_on_time for loan in active_loans)
    total_tenure = sum(loan.tenure for loan in active_loans)
    
    if total_emis_on_time < 0.9 * total_tenure:
        credit_score -= 30
    elif total_emis_on_time < 0.8 * total_tenure:
        credit_score -= 50
    elif total_emis_on_time < 0.7 * total_tenure:
        credit_score -= 70
    elif total_emis_on_time < 0.5 * total_tenure:
        credit_score -= 90
    
    # approving loan and calculating interest    
    calculated_interest = 0
    corrected_interest_rate = 0        
    if credit_score >= 50:
        calculated_interest = interest_rate
        corrected_interest_rate = interest_rate
    elif credit_score < 50 and credit_score >= 30:
        if interest_rate >12 and interest_rate < 16:
            corrected_interest_rate = interest_rate
            calculated_interest = interest_rate
        else:
            calculated_interest = 12 + (100-credit_score)/100
            corrected_interest_rate = calculated_interest - interest_rate
    elif credit_score < 30 and credit_score >= 10:
        if interest_rate >16:
            corrected_interest_rate = interest_rate
            calculated_interest = interest_rate
        else:
            calculated_interest = 16 + (100-credit_score)/100
            corrected_interest_rate = calculated_interest - interest_rate
    else:
        response_data={
            'customer_id':customer.customer_id,
            'approval':False
        }
        return response_data
    
    # calculate monthly installment
    monthly_installment = (request_amount * calculated_interest * (1+calculated_interest)**tenure) / ((1+calculated_interest)**tenure - 1)
    response_data={
        'customer_id':customer.customer_id,
        'approval':True,
        'interest_rate':calculated_interest,
        'corrected_interest_rate':corrected_interest_rate,
        'tenure':tenure,
        'monthly_installment':monthly_installment
    }
    return response_data

@api_view(['POST'])
def check_loan_eligibility(request):
    try:
        customer_id = request.data.get('customer_id')
        request_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')
        
        customer = Customer.objects.get(customer_id=customer_id)
        non_active_loans = Loan.objects.filter(customer=customer, end_date__lt=date.today())
        active_loans = Loan.objects.filter(customer=customer, end_date__gt=date.today())
        
        response_data = calculate_loan_eligibility(customer,non_active_loans,active_loans,request_amount,interest_rate,tenure)    
        return Response(response_data, status=status.HTTP_200_OK)

    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
# for active loans (end date > current data)
# compare total emi with monthly salary
# compare total loan amount with approved amount
# calculate months between today and start date
# emis_paid_on_time < 80% of total emis - 10

# for non active loans (end date < current date)
# count of loans paid on time : emis_paid_on_time == tenure
# if < 90% then 70 
# if < 80% then 50
# if < 70% then 30
# if < 50% then 10
