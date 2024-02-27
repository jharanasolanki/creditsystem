from datetime import date, timedelta
from django.shortcuts import render
from .models import Loan,Customer
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LoanSerializer
from customer.views import calculate_loan_eligibility
import pandas as pd

# Create your views here.
def ingest_excel_data(file_path):
    try:
        # Read Excel file using pandas
        df = pd.read_excel(file_path)

        # Iterate over rows and create Loan objects
        for index, row in df.iterrows():
            customer_id = row['Customer ID']
            customer = Customer.objects.get(customer_id=customer_id)
            loan = Loan(
                customer = customer,
                loan_id = row['Loan ID'],
                loan_amount = row['Loan Amount'],
                tenure = row['Tenure'],
                interest_rate = row['Interest Rate'],
                monthly_repayment = row['Monthly payment'],
                emis_paid_on_time = row['EMIs paid on Time'],
                start_date = row['Date of Approval'],
                end_date = row['End Date']
            )
            loan.save()
        
        # Optionally, perform any additional processing/logging
    except Exception as e:
        # Handle error
        print(f"Error ingesting Excel data: {e}")

class LoanCreate(generics.CreateAPIView):
    """
    API endpoint that allows creation of a new loan.
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            response_data = {
                'loan_id': serializer.data['loan_id'],
                'Loan': serializer.data['Loan'],
                'loan_amount': serializer.data['loan_amount'],
                'tenure': serializer.data['tenure'],
                'interest_rate': serializer.data['interest_rate'],
                'monthly_repayment': serializer.data['monthly_repayment'],
                'emis_paid_on_time': serializer.data['emis_paid_on_time'],
                'start_date': serializer.data['start_date'],
                'end_date': serializer.data['end_date']
            }
            # Customize the response status code and headers if needed
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
class LoanList(generics.ListAPIView):
    # API endpoint that allows Loan to be viewed.
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class LoanDetail(generics.RetrieveAPIView):
    # API endpoint that returns a single Loan by pk.
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    
class LoanListByCustomer(generics.ListAPIView):
    # API endpoint that returns Loan List by customer id.
    serializer_class = LoanSerializer

    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')
        queryset = Loan.objects.filter(customer_id=customer_id)
        return queryset
    
class LoanUpdate(generics.RetrieveUpdateAPIView):
    # API endpoint that allows a Loan record to be updated.
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    
class LoanDelete(generics.RetrieveDestroyAPIView):
    # API endpoint that allows a Loan record to be deleted.
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    
@api_view(['POST'])
def create_loan(request):
    try:
        customer_id = request.data.get('customer_id')
        request_amount = request.data.get('loan_amount')
        interest_rate = request.data.get('interest_rate')
        tenure = request.data.get('tenure')
        
        customer = Customer.objects.get(customer_id=customer_id)
        non_active_loans = Loan.objects.filter(customer=customer, end_date__lt=date.today())
        active_loans = Loan.objects.filter(customer=customer, end_date__gt=date.today())
        
        response_data = calculate_loan_eligibility(customer,non_active_loans,active_loans,request_amount,interest_rate,tenure)
        if response_data["approval"]:
            start_date = date.today().strftime('%Y-%m-%d')
            end_date = (date.today() + timedelta(days=30 * tenure)).strftime('%Y-%m-%d')
            new_loan = Loan(
                customer = customer,
                loan_amount=request_amount,  
                tenure=tenure,  
                interest_rate=response_data["interest_rate"], 
                monthly_repayment=response_data["monthly_installment"],  
                emis_paid_on_time=0,  
                start_date= start_date,
                end_date= end_date
            )
            new_loan.save()
            client_response = {
                'loan_id': new_loan.loan_id,
                'customer_id': customer_id,
                'loan_approved': True,
                'monthly_installment':response_data["monthly_installment"]
            }
        else:
            client_response = {
                'customer_id': customer_id,
                'loan_approved': False,
                'message':'Insufficient Credit Score'
            }
        # Customize the response status code and headers if needed
        return Response(client_response, status=status.HTTP_201_CREATED)
            
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        