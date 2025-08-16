@echo off
echo 🎨 Starting QCanvas Frontend...
echo.

cd frontend

echo 📦 Checking Node.js dependencies...
if not exist node_modules (
    echo Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo 🚀 Starting development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop
echo.

npm run dev

echo.
echo 👋 Frontend stopped
pause
