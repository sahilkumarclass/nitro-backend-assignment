from rest_framework import serializers
from .models import File


class FileUploadSerializer(serializers.ModelSerializer):
    """Serializer for file upload"""
    
    class Meta:
        model = File
        fields = ['id', 'filename', 'original_filename', 'file_size', 'file_type', 'status', 'created_at']
        read_only_fields = ['id', 'filename', 'file_size', 'file_type', 'status', 'created_at']


class FileProgressSerializer(serializers.ModelSerializer):
    """Serializer for file progress tracking"""
    
    class Meta:
        model = File
        fields = ['id', 'status', 'progress']


class FileListSerializer(serializers.ModelSerializer):
    """Serializer for listing files"""
    
    class Meta:
        model = File
        fields = ['id', 'original_filename', 'file_size', 'file_type', 'status', 'created_at']


class FileDetailSerializer(serializers.ModelSerializer):
    """Serializer for file details and parsed content"""
    
    class Meta:
        model = File
        fields = [
            'id', 'original_filename', 'file_size', 'file_type', 
            'status', 'progress', 'parsed_content', 'error_message', 
            'created_at', 'updated_at'
        ]


class FileUploadResponseSerializer(serializers.ModelSerializer):
    """Serializer for file upload response"""
    
    message = serializers.CharField(default="File uploaded successfully")
    
    class Meta:
        model = File
        fields = ['id', 'message', 'status']
