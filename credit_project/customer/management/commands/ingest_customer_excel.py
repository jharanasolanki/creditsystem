import os
from django.core.management.base import BaseCommand
from customer.views import ingest_excel_data

class Command(BaseCommand):
    help = 'Ingest data from Excel file'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        file_path = os.path.join(base_dir, 'excel_folder', 'customer_data.xlsx')
        
        ingest_excel_data(file_path)
        self.stdout.write(self.style.SUCCESS('Data ingestion started'))