import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Attendance
from django.utils import timezone
import os

class Command(BaseCommand):
    help = 'Export attendance records to an Excel file'

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, help='Filter by date (YYYY-MM-DD)')
        parser.add_argument('--filename', type=str, default='exported_attendance.xlsx', help='Output filename')

    def handle(self, *args, **options):
        date_str = options['date']
        filename = options['filename']

        queryset = Attendance.objects.all()
        if date_str:
            queryset = queryset.filter(date=date_str)

        if not queryset.exists():
            self.stdout.write(self.style.WARNING('No attendance records found for the given criteria.'))
            return

        data = []
        for record in queryset:
            data.append({
                'Student Name': record.student.name,
                'Status': record.status,
                'Date': record.date,
                'Time': record.time,
            })

        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

        self.stdout.write(self.style.SUCCESS(f'Successfully exported {len(data)} records to {filename}'))
