import os
from rest_framework import status, generics
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from .models import File
from .serializers import (
    FileUploadSerializer, FileProgressSerializer, FileListSerializer,
    FileDetailSerializer, FileUploadResponseSerializer
)
from .tasks import process_file_upload


class FileUploadView(APIView):
    """Handle file uploads with progress tracking"""
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request, *args, **kwargs):
        try:
            # Get the uploaded file
            uploaded_file = request.FILES.get('file')
            
            if not uploaded_file:
                return Response(
                    {'error': 'No file provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate file size
            if uploaded_file.size > settings.MAX_FILE_SIZE:
                return Response(
                    {'error': f'File size exceeds maximum limit of {settings.MAX_FILE_SIZE} bytes'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get file extension
            file_extension = os.path.splitext(uploaded_file.name)[1].lower().lstrip('.')
            
            # Validate file type
            allowed_extensions = ['csv', 'xlsx', 'xls', 'pdf', 'txt']
            if file_extension not in allowed_extensions:
                return Response(
                    {'error': f'File type {file_extension} is not supported. Allowed types: {", ".join(allowed_extensions)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create file record
            file_obj = File.objects.create(
                filename=f"{uploaded_file.name}_{uploaded_file.size}",
                original_filename=uploaded_file.name,
                file_path=uploaded_file,
                file_size=uploaded_file.size,
                file_type=file_extension,
                status='uploading'
            )
            
            # Start background processing
            process_file_upload.delay(str(file_obj.id))
            
            # Return response
            serializer = FileUploadResponseSerializer(file_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Upload failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileProgressView(APIView):
    """Get file upload/processing progress"""
    
    def get(self, request, file_id, *args, **kwargs):
        try:
            file_obj = get_object_or_404(File, id=file_id)
            serializer = FileProgressSerializer(file_obj)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Error retrieving progress: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileListView(generics.ListAPIView):
    """List all uploaded files with metadata"""
    queryset = File.objects.all()
    serializer_class = FileListSerializer
    pagination_class = None  # Disable pagination for this endpoint


class FileDetailView(APIView):
    """Get file details and parsed content"""
    
    def get(self, request, file_id, *args, **kwargs):
        try:
            file_obj = get_object_or_404(File, id=file_id)
            
            # Check if file is ready
            if file_obj.status != 'ready':
                return Response({
                    'message': 'File upload or processing in progress. Please try again later.',
                    'status': file_obj.status,
                    'progress': file_obj.progress
                }, status=status.HTTP_202_ACCEPTED)
            
            # Return parsed content
            serializer = FileDetailSerializer(file_obj)
            return Response(serializer.data)
            
        except Exception as e:
            return Response(
                {'error': f'Error retrieving file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FileDeleteView(APIView):
    """Delete a file and its parsed content"""
    
    def delete(self, request, file_id, *args, **kwargs):
        try:
            file_obj = get_object_or_404(File, id=file_id)
            
            # Delete file from storage
            file_obj.delete_file_from_storage()
            
            # Delete database record
            file_obj.delete()
            
            return Response(
                {'message': 'File deleted successfully'}, 
                status=status.HTTP_204_NO_CONTENT
            )
            
        except Exception as e:
            return Response(
                {'error': f'Error deleting file: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'message': 'File Parser API is running'
    })
