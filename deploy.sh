#!/bin/bash

# Reflektor Deployment Script
# Ez a script segít a gyors deploymentben

echo "🚀 Reflektor Deployment Script"
echo "================================"

# Ellenőrizzük a Docker telepítését
if ! command -v docker &> /dev/null; then
    echo "❌ Docker nincs telepítve"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose nincs telepítve"
    exit 1
fi

# Ellenőrizzük a .env fájlt
if [ ! -f .env ]; then
    echo "⚠️  .env fájl nem található, létrehozom a .env.example alapján..."
    cp .env.example .env
    echo "📝 Kérlek, add meg az OpenAI API kulcsot a .env fájlban!"
    echo "   OPENAI_API_KEY=sk-your-key-here"
    exit 1
fi

# Ellenőrizzük az API kulcsot
if grep -q "sk-your-key-here" .env; then
    echo "❌ Kérlek, add meg a valós OpenAI API kulcsot a .env fájlban!"
    exit 1
fi

echo "✅ Ellenőrzés sikeres"

# Build és start
echo "🔨 Docker image-ek építése..."
docker-compose build

echo "🚀 Containerek indítása..."
docker-compose up -d

echo "⏳ Várakozás a szerver indulására..."
sleep 10

# Health check
echo "🔍 Health check..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend sikeresen fut a http://localhost:8000 címen"
else
    echo "❌ Backend nem érhető el"
    docker-compose logs backend
    exit 1
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend sikeresen fut a http://localhost:3000 címen"
else
    echo "❌ Frontend nem érhető el"
    docker-compose logs frontend
    exit 1
fi

echo ""
echo "🎉 Deployment sikeres!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "A deployment leállításához: docker-compose down"
echo "Logok megtekintéséhez: docker-compose logs -f"
