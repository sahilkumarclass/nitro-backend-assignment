from django.urls import path
from .views import (
    FileUploadView, FileProgressView, FileListView, 
    FileDetailView, FileDeleteView, health_check
)

app_name = 'files'

urlpatterns = [
    path('', FileListView.as_view(), name='file-list'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('<uuid:file_id>/', FileDetailView.as_view(), name='file-detail'),
    path('<uuid:file_id>/progress/', FileProgressView.as_view(), name='file-progress'),
    path('<uuid:file_id>/delete/', FileDeleteView.as_view(), name='file-delete'),
    path('health/', health_check, name='health-check'),
]
