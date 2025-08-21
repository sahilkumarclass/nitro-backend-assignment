#!/usr/bin/env python3
"""
Test script for the File Parser API
This script demonstrates all the API endpoints and functionality
"""

import requests
import time
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/api/files"
SAMPLE_FILES_DIR = "sample_data"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_file_upload(file_path):
    """Test file upload endpoint"""
    print(f"📤 Testing File Upload: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/upload/", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        return response.json().get('id')
    return None

def test_get_progress(file_id):
    """Test progress tracking endpoint"""
    print(f"📊 Testing Progress Tracking for file: {file_id}")
    response = requests.get(f"{BASE_URL}/{file_id}/progress/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_list_files():
    """Test list files endpoint"""
    print("📋 Testing List Files...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_get_file_details(file_id):
    """Test get file details endpoint"""
    print(f"📄 Testing Get File Details for file: {file_id}")
    response = requests.get(f"{BASE_URL}/{file_id}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_delete_file(file_id):
    """Test delete file endpoint"""
    print(f"🗑️ Testing Delete File for file: {file_id}")
    response = requests.delete(f"{BASE_URL}/{file_id}/delete/")
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("File deleted successfully")
    else:
        print(f"Response: {response.text}")
    print()

def wait_for_processing(file_id, max_wait=60):
    """Wait for file processing to complete"""
    print(f"⏳ Waiting for file processing to complete...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/{file_id}/progress/")
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            progress = data.get('progress', 0)
            
            print(f"Status: {status}, Progress: {progress}%")
            
            if status == 'ready':
                print("✅ File processing completed!")
                return True
            elif status == 'failed':
                print("❌ File processing failed!")
                return False
        
        time.sleep(2)
    
    print("⏰ Timeout waiting for processing")
    return False

def main():
    """Main test function"""
    print("🚀 Starting File Parser API Tests")
    print("=" * 50)
    
    # Test health check
    test_health_check()
    
    # Test file uploads
    uploaded_files = []
    
    # Test CSV upload
    csv_file = os.path.join(SAMPLE_FILES_DIR, "sample.csv")
    if os.path.exists(csv_file):
        file_id = test_file_upload(csv_file)
        if file_id:
            uploaded_files.append(file_id)
            print()
    
    # Test TXT upload
    txt_file = os.path.join(SAMPLE_FILES_DIR, "sample.txt")
    if os.path.exists(txt_file):
        file_id = test_file_upload(txt_file)
        if file_id:
            uploaded_files.append(file_id)
            print()
    
    # Wait for processing and test progress
    for file_id in uploaded_files:
        test_get_progress(file_id)
        if wait_for_processing(file_id):
            test_get_file_details(file_id)
        print()
    
    # Test list files
    test_list_files()
    
    # Test delete files
    for file_id in uploaded_files:
        test_delete_file(file_id)
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()
