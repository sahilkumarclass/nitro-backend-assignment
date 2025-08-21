import os
import time
from celery import shared_task
from django.conf import settings
from .models import File
from .parsers import parse_file


@shared_task(bind=True)
def process_file_upload(self, file_id: str):
    """Background task to process file upload and parsing"""
    try:
        # Get the file object
        file_obj = File.objects.get(id=file_id)
        
        # Update status to processing
        file_obj.mark_as_processing()
        
        # Simulate upload progress (in real scenario, this would be tracked during upload)
        for progress in range(0, 101, 10):
            file_obj.update_progress(progress)
            time.sleep(0.5)  # Simulate processing time
        
        # Parse the file
        file_path = file_obj.file_path.path
        file_type = file_obj.get_file_extension().lstrip('.')
        
        try:
            parsed_content = parse_file(file_path, file_type)
            file_obj.mark_as_ready(parsed_content)
            
        except Exception as parse_error:
            file_obj.mark_as_failed(str(parse_error))
            
    except File.DoesNotExist:
        print(f"File with ID {file_id} not found")
    except Exception as e:
        print(f"Error processing file {file_id}: {str(e)}")
        try:
            file_obj = File.objects.get(id=file_id)
            file_obj.mark_as_failed(str(e))
        except:
            pass


@shared_task
def cleanup_failed_files():
    """Clean up files that have been in failed status for more than 24 hours"""
    from django.utils import timezone
    from datetime import timedelta
    
    cutoff_time = timezone.now() - timedelta(hours=24)
    failed_files = File.objects.filter(
        status='failed',
        created_at__lt=cutoff_time
    )
    
    for file_obj in failed_files:
        file_obj.delete_file_from_storage()
        file_obj.delete()
    
    return f"Cleaned up {failed_files.count()} failed files"


@shared_task
def update_file_progress(file_id: str, progress: int):
    """Update file progress"""
    try:
        file_obj = File.objects.get(id=file_id)
        file_obj.update_progress(progress)
    except File.DoesNotExist:
        print(f"File with ID {file_id} not found")
