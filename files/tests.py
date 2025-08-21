import os
import tempfile
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import File


class FileModelTest(TestCase):
    """Test cases for the File model"""
    
    def setUp(self):
        """Set up test data"""
        self.test_file = SimpleUploadedFile(
            "test.csv",
            b"Name,Age\nJohn,30\nJane,25",
            content_type="text/csv"
        )
    
    def test_file_creation(self):
        """Test file creation"""
        file_obj = File.objects.create(
            filename="test.csv",
            original_filename="test.csv",
            file_path=self.test_file,
            file_size=100,
            file_type="csv",
            status="uploading"
        )
        
        self.assertEqual(file_obj.original_filename, "test.csv")
        self.assertEqual(file_obj.file_type, "csv")
        self.assertEqual(file_obj.status, "uploading")
        self.assertEqual(file_obj.progress, 0)
    
    def test_file_status_updates(self):
        """Test file status update methods"""
        file_obj = File.objects.create(
            filename="test.csv",
            original_filename="test.csv",
            file_path=self.test_file,
            file_size=100,
            file_type="csv"
        )
        
        # Test mark as processing
        file_obj.mark_as_processing()
        self.assertEqual(file_obj.status, "processing")
        self.assertEqual(file_obj.progress, 0)
        
        # Test update progress
        file_obj.update_progress(50)
        self.assertEqual(file_obj.progress, 50)
        
        # Test mark as ready
        file_obj.mark_as_ready({"data": "test"})
        self.assertEqual(file_obj.status, "ready")
        self.assertEqual(file_obj.progress, 100)
        self.assertEqual(file_obj.parsed_content, {"data": "test"})
        
        # Test mark as failed
        file_obj.mark_as_failed("Test error")
        self.assertEqual(file_obj.status, "failed")
        self.assertEqual(file_obj.error_message, "Test error")
    
    def test_file_extension(self):
        """Test file extension extraction"""
        file_obj = File.objects.create(
            filename="test.csv",
            original_filename="test.csv",
            file_path=self.test_file,
            file_size=100,
            file_type="csv"
        )
        
        self.assertEqual(file_obj.get_file_extension(), ".csv")


class FileAPITest(APITestCase):
    """Test cases for the File API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.upload_url = reverse('files:file-upload')
        self.list_url = reverse('files:file-list')
        self.health_url = reverse('files:health-check')
        
        # Create test file
        self.test_file_content = b"Name,Age\nJohn,30\nJane,25"
        self.test_file = SimpleUploadedFile(
            "test.csv",
            self.test_file_content,
            content_type="text/csv"
        )
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'healthy')
    
    def test_file_upload(self):
        """Test file upload endpoint"""
        data = {'file': self.test_file}
        response = self.client.post(self.upload_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = response.json()
        self.assertIn('id', response_data)
        self.assertEqual(response_data['status'], 'uploading')
    
    def test_file_upload_no_file(self):
        """Test file upload without file"""
        response = self.client.post(self.upload_url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_file_upload_invalid_type(self):
        """Test file upload with invalid file type"""
        invalid_file = SimpleUploadedFile(
            "test.exe",
            b"invalid content",
            content_type="application/octet-stream"
        )
        data = {'file': invalid_file}
        response = self.client.post(self.upload_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_list_files(self):
        """Test list files endpoint"""
        # Create a test file
        file_obj = File.objects.create(
            filename="test.csv",
            original_filename="test.csv",
            file_path=self.test_file,
            file_size=100,
            file_type="csv",
            status="ready"
        )
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['original_filename'], 'test.csv')
    
    def test_file_progress(self):
        """Test file progress endpoint"""
        file_obj = File.objects.create(
            filename="test.csv",
            original_filename="test.csv",
            file_path=self.test_file,
            file_size=100,
            file_type="csv",
            status="processing",
            progress=50
        )
        
        progress_url = reverse('files:file-progress', kwargs={'file_id': file_obj.id})
        response = self.client.get(progress_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'processing')
        self.assertEqual(data['progress'], 50)
    
    def test_file_details_ready(self):
        """Test file details endpoint when file is ready"""
        file_obj = File.objects.create(
            filename="test.csv",
            original_filename="test.csv",
            file_path=self.test_file,
            file_size=100,
            file_type="csv",
            status="ready",
            progress=100,
            parsed_content={"type": "csv", "rows": 2}
        )
        
        detail_url = reverse('files:file-detail', kwargs={'file_id': file_obj.id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['status'], 'ready')
        self.assertEqual(data['parsed_content']['type'], 'csv')
    
    def test_file_details_processing(self):
        """Test file details endpoint when file is processing"""
        file_obj = File.objects.create(
            filename="test.csv",
            original_filename="test.csv",
            file_path=self.test_file,
            file_size=100,
            file_type="csv",
            status="processing",
            progress=50
        )
        
        detail_url = reverse('files:file-detail', kwargs={'file_id': file_obj.id})
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        data = response.json()
        self.assertIn('message', data)
        self.assertEqual(data['status'], 'processing')
    
    def test_delete_file(self):
        """Test file delete endpoint"""
        file_obj = File.objects.create(
            filename="test.csv",
            original_filename="test.csv",
            file_path=self.test_file,
            file_size=100,
            file_type="csv"
        )
        
        delete_url = reverse('files:file-delete', kwargs={'file_id': file_obj.id})
        response = self.client.delete(delete_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(File.objects.filter(id=file_obj.id).exists())
    
    def test_file_not_found(self):
        """Test endpoints with non-existent file ID"""
        import uuid
        fake_id = uuid.uuid4()
        
        # Test progress endpoint
        progress_url = reverse('files:file-progress', kwargs={'file_id': fake_id})
        response = self.client.get(progress_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test detail endpoint
        detail_url = reverse('files:file-detail', kwargs={'file_id': fake_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
        # Test delete endpoint
        delete_url = reverse('files:file-delete', kwargs={'file_id': fake_id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
