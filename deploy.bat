@echo off
REM Reflektor Deployment Script for Windows

echo 🚀 Reflektor Deployment Script
echo ================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker nincs telepítve
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose nincs telepítve
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env fájl nem található, létrehozom a .env.example alapján...
    copy .env.example .env
    echo 📝 Kérlek, add meg az OpenAI API kulcsot a .env fájlban!
    echo    OPENAI_API_KEY=sk-your-key-here
    pause
    exit /b 1
)

REM Check if API key is set
findstr /C:"sk-your-key-here" .env >nul
if %errorlevel% equ 0 (
    echo ❌ Kérlek, add meg a valós OpenAI API kulcsot a .env fájlban!
    pause
    exit /b 1
)

echo ✅ Ellenőrzés sikeres

REM Build and start
echo 🔨 Docker image-ek építése...
docker-compose build

echo 🚀 Containerek indítása...
docker-compose up -d

echo ⏳ Várakozás a szerver indulására...
timeout /t 10 /nobreak >nul

REM Health check
echo 🔍 Health check...
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend sikeresen fut a http://localhost:8000 címen
) else (
    echo ❌ Backend nem érhető el
    docker-compose logs backend
    pause
    exit /b 1
)

curl -f http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend sikeresen fut a http://localhost:3000 címen
) else (
    echo ❌ Frontend nem érhető el
    docker-compose logs frontend
    pause
    exit /b 1
)

echo.
echo 🎉 Deployment sikeres!
echo 📱 Frontend: http://localhost:3000
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo A deployment leállításához: docker-compose down
echo Logok megtekintéséhez: docker-compose logs -f
pause
