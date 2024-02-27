import pandas as pd
from celery import shared_task
from .models import Customer

@shared_task
def ingest_excel_data(file_path):
    try:
        # Read Excel file using pandas
        df = pd.read_excel(file_path)

        # Iterate over rows and create Customer objects
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
        
        # Optionally, perform any additional processing/logging
    except Exception as e:
        # Handle error
        print(f"Error ingesting Excel data: {e}")
