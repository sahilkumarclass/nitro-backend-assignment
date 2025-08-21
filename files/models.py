import os
import uuid
from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings


class File(models.Model):
    """Model for storing file uploads and their metadata"""
    
    STATUS_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255)
    original_filename = models.CharField(max_length=255)
    file_path = models.FileField(
        upload_to='uploads/',
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx', 'xls', 'pdf', 'txt'])]
    )
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploading')
    progress = models.IntegerField(default=0)
    parsed_content = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'files'
    
    def __str__(self):
        return f"{self.original_filename} ({self.id})"
    
    def get_file_extension(self):
        """Get file extension from filename"""
        return os.path.splitext(self.original_filename)[1].lower()
    
    def update_progress(self, progress):
        """Update upload/processing progress"""
        self.progress = progress
        if progress >= 100:
            self.status = 'ready'
        self.save(update_fields=['progress', 'status'])
    
    def mark_as_processing(self):
        """Mark file as processing"""
        self.status = 'processing'
        self.progress = 0
        self.save(update_fields=['status', 'progress'])
    
    def mark_as_failed(self, error_message=""):
        """Mark file as failed with error message"""
        self.status = 'failed'
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message'])
    
    def mark_as_ready(self, parsed_content=None):
        """Mark file as ready with parsed content"""
        self.status = 'ready'
        self.progress = 100
        if parsed_content:
            self.parsed_content = parsed_content
        self.save(update_fields=['status', 'progress', 'parsed_content'])
    
    def delete_file_from_storage(self):
        """Delete the actual file from storage"""
        if self.file_path and os.path.exists(self.file_path.path):
            os.remove(self.file_path.path)
