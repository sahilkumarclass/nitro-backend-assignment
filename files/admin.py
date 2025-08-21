from django.contrib import admin
from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'original_filename', 'file_type', 'file_size', 'status', 'progress', 'created_at']
    list_filter = ['status', 'file_type', 'created_at']
    search_fields = ['original_filename', 'filename']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('File Information', {
            'fields': ('id', 'original_filename', 'filename', 'file_path', 'file_size', 'file_type')
        }),
        ('Status & Progress', {
            'fields': ('status', 'progress', 'error_message')
        }),
        ('Content', {
            'fields': ('parsed_content',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Files should only be created through API uploads
