from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from files.models import File
from files.tasks import process_file_upload
import uuid


class Command(BaseCommand):
    help = 'Test the File Parser API functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file-type',
            type=str,
            default='csv',
            help='Type of test file to create (csv, txt)'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting File Parser API Test')
        )

        file_type = options['file_type']
        
        # Create test file content based on type
        if file_type == 'csv':
            content = b"Name,Age,City\nJohn,30,New York\nJane,25,San Francisco"
            filename = "test.csv"
            content_type = "text/csv"
        elif file_type == 'txt':
            content = b"This is a test text file.\nIt has multiple lines.\nFor testing the API."
            filename = "test.txt"
            content_type = "text/plain"
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Unsupported file type: {file_type}')
            )
            return

        # Create test file
        test_file = SimpleUploadedFile(
            filename,
            content,
            content_type=content_type
        )

        # Create file record
        file_obj = File.objects.create(
            filename=filename,
            original_filename=filename,
            file_path=test_file,
            file_size=len(content),
            file_type=file_type,
            status='uploading'
        )

        self.stdout.write(
            self.style.SUCCESS(f'✅ Created test file: {filename} (ID: {file_obj.id})')
        )

        # Start processing
        self.stdout.write('🔄 Starting file processing...')
        process_file_upload.delay(str(file_obj.id))

        # Monitor progress
        self.stdout.write('📊 Monitoring progress...')
        import time
        for i in range(10):  # Monitor for 20 seconds
            file_obj.refresh_from_db()
            self.stdout.write(
                f'Status: {file_obj.status}, Progress: {file_obj.progress}%'
            )
            
            if file_obj.status == 'ready':
                self.stdout.write(
                    self.style.SUCCESS('✅ File processing completed!')
                )
                break
            elif file_obj.status == 'failed':
                self.stdout.write(
                    self.style.ERROR(f'❌ File processing failed: {file_obj.error_message}')
                )
                break
            
            time.sleep(2)

        # Show final result
        file_obj.refresh_from_db()
        self.stdout.write(
            self.style.SUCCESS(f'📄 Final Status: {file_obj.status}')
        )
        
        if file_obj.parsed_content:
            self.stdout.write(
                self.style.SUCCESS(f'📊 Parsed Content: {file_obj.parsed_content}')
            )

        self.stdout.write(
            self.style.SUCCESS('🎉 Test completed!')
        )
