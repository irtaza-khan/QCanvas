#!/bin/bash

echo "🎨 Starting QCanvas Frontend..."
echo

cd frontend

echo "📦 Checking Node.js dependencies..."
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

echo
echo "🚀 Starting development server..."
echo "Frontend will be available at: http://localhost:3000"
echo "Press Ctrl+C to stop"
echo

npm run dev

echo
echo "👋 Frontend stopped"
