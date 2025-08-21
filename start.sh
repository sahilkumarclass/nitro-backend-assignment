#!/bin/bash

# File Parser API Startup Script

echo "🚀 Starting File Parser API..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create media directory if it doesn't exist
mkdir -p media/uploads

# Start all services using Docker Compose
echo "📦 Starting services with Docker Compose..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose exec -T web python manage.py migrate

echo "✅ File Parser API is ready!"
echo ""
echo "🌐 API Base URL: http://localhost:8000/api/files/"
echo "🔧 Admin Interface: http://localhost:8000/admin/"
echo "📊 Health Check: http://localhost:8000/api/files/health/"
echo ""
echo "📚 Check README.md for API documentation and usage examples."
echo ""
echo "To stop the services, run: docker-compose down"
