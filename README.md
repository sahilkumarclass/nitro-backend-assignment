# File Parser CRUD API

A comprehensive Django-based backend application that supports uploading, storing, parsing, and retrieving files with real-time progress tracking for large uploads.

## Features

- **File Upload**: Support for CSV, Excel, PDF, and TXT files with size validation
- **Progress Tracking**: Real-time upload and processing progress monitoring
- **File Parsing**: Automatic parsing of uploaded files using appropriate libraries
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Background Processing**: Asynchronous file processing using Celery
- **Database Support**: PostgreSQL for metadata and MongoDB for parsed content
- **RESTful API**: Clean REST API design with proper status codes
- **Docker Support**: Complete containerization with Docker Compose

## Tech Stack

- **Backend**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: PostgreSQL 15 (metadata) + MongoDB 6.0 (parsed content)
- **Task Queue**: Celery 5.3.4 + Redis 7
- **File Parsing**: pandas, openpyxl, PyPDF2
- **Containerization**: Docker & Docker Compose
- **CORS**: django-cors-headers

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

## Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd file-parser-api
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Access the API**
   - API Base URL: http://localhost:8000/api/files/
   - Admin Interface: http://localhost:8000/admin/

### Manual Setup

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd file-parser-api
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment setup**
   ```bash
   cp env.example .env
   # Edit .env with your database credentials
   ```

3. **Database setup**
   ```bash
   # Start PostgreSQL and MongoDB (using Docker or local installation)
   python3 manage.py migrate
   python3 manage.py createsuperuser
   ```

4. **Start services**
   ```bash
   # Terminal 1: Start Redis
   redis-server
   
   # Terminal 2: Start Celery worker
   celery -A file_parser worker --loglevel=info
   
   # Terminal 3: Start Django server
   python3 manage.py runserver
   ```

## API Documentation

### Base URL
```
http://localhost:8000/api/files/
```

### Endpoints

#### 1. Upload File
**POST** `/upload/`

Upload a file for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` field containing the file

**Response:**
```json
{
  "id": "uuid",
  "message": "File uploaded successfully",
  "status": "uploading"
}
```

#### 2. Get Upload Progress
**GET** `/files/{file_id}/progress/`

Get the current progress of file upload/processing.

**Response:**
```json
{
  "id": "uuid",
  "status": "processing",
  "progress": 42
}
```

#### 3. List All Files
**GET** `/`

Get a list of all uploaded files with metadata.

**Response:**
```json
[
  {
    "id": "uuid",
    "original_filename": "sample.csv",
    "file_size": 1024,
    "file_type": "csv",
    "status": "ready",
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

#### 4. Get File Details
**GET** `/files/{file_id}/`

Get file details and parsed content (if ready).

**Response (if ready):**
```json
{
  "id": "uuid",
  "original_filename": "sample.csv",
  "file_size": 1024,
  "file_type": "csv",
  "status": "ready",
  "progress": 100,
  "parsed_content": {
    "type": "csv",
    "rows": 100,
    "columns": 5,
    "column_names": ["col1", "col2", "col3", "col4", "col5"],
    "data": [...],
    "summary": {...}
  },
  "created_at": "2024-01-01T12:00:00Z",
  "updated_at": "2024-01-01T12:01:00Z"
}
```

**Response (if processing):**
```json
{
  "message": "File upload or processing in progress. Please try again later.",
  "status": "processing",
  "progress": 50
}
```

#### 5. Delete File
**DELETE** `/files/{file_id}/delete/`

Delete a file and its parsed content.

**Response:**
```json
{
  "message": "File deleted successfully"
}
```

#### 6. Health Check
**GET** `/health/`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "message": "File Parser API is running"
}
```

## File Types Supported

| File Type | Extension | Parser | Features |
|-----------|-----------|--------|----------|
| CSV | `.csv` | pandas | Rows, columns, data preview |
| Excel | `.xlsx`, `.xls` | openpyxl | Multiple sheets, data preview |
| PDF | `.pdf` | PyPDF2 | Text extraction, page count |
| Text | `.txt` | Built-in | Line count, character count |

## File Size Limits

- **Maximum file size**: 100MB (configurable in settings)
- **Supported formats**: CSV, Excel (xlsx, xls), PDF, TXT

## Progress Tracking

The API provides real-time progress tracking through:

1. **Upload Progress**: Tracks file upload completion
2. **Processing Progress**: Tracks file parsing progress
3. **Status Updates**: Real-time status changes (uploading → processing → ready/failed)

## Background Processing

File processing is handled asynchronously using Celery:

- **Upload**: File is saved and processing task is queued
- **Processing**: File is parsed in background with progress updates
- **Completion**: Parsed content is stored and status updated

## Database Schema

### PostgreSQL (Metadata)
```sql
CREATE TABLE files (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    file_path VARCHAR(255),
    file_size BIGINT,
    file_type VARCHAR(10),
    status VARCHAR(20),
    progress INTEGER,
    parsed_content JSONB,
    error_message TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### MongoDB (Parsed Content)
Parsed content is stored as JSON documents with the following structure:
- File metadata
- Parsed data (rows, columns, text content, etc.)
- Processing statistics

## Environment Variables

Create a `.env` file with the following variables:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
POSTGRES_DB=file_parser_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# MongoDB Settings
MONGO_DB_NAME=file_parser_mongo
MONGO_USERNAME=admin
MONGO_PASSWORD=admin123
MONGO_HOST=localhost
MONGO_PORT=27017

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379

# File Upload Settings
MAX_FILE_SIZE=104857600
UPLOAD_DIR=media/uploads/
```

## Testing

### Using curl

1. **Upload a file:**
   ```bash
   curl -X POST -F "file=@sample.csv" http://localhost:8000/api/files/upload/
   ```

2. **Check progress:**
   ```bash
   curl http://localhost:8000/api/files/{file_id}/progress/
   ```

3. **Get file details:**
   ```bash
   curl http://localhost:8000/api/files/{file_id}/
   ```

4. **List all files:**
   ```bash
   curl http://localhost:8000/api/files/
   ```

### Using Postman

Import the provided Postman collection for easy testing.

## Development

### Running Tests
```bash
python3 manage.py test
```

### Code Style
```bash
# Install pre-commit hooks
pre-commit install
```

### Database Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

## Production Deployment

1. **Update settings for production**
   - Set `DEBUG=False`
   - Configure proper database credentials
   - Set up static file serving
   - Configure logging

2. **Use Gunicorn**
   ```bash
   gunicorn file_parser.wsgi:application --bind 0.0.0.0:8000
   ```

3. **Set up Celery for production**
   ```bash
   celery -A file_parser worker --loglevel=info
   celery -A file_parser beat --loglevel=info
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Ensure PostgreSQL and MongoDB are running
   - Check connection credentials in `.env`

2. **Celery Worker Not Starting**
   - Ensure Redis is running
   - Check Celery configuration in settings

3. **File Upload Fails**
   - Check file size limits
   - Verify file type is supported
   - Ensure media directory is writable

### Logs

Check logs for debugging:
```bash
# Django logs
docker-compose logs web

# Celery logs
docker-compose logs celery

# Database logs
docker-compose logs postgres
docker-compose logs mongodb
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on GitHub.
