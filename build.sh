#!/bin/bash

# Build script for Kalori Makanan API React frontend
# This script builds the React TypeScript app and copies it to FastAPI static folder

set -e  # Exit on any error

echo "🚀 Building Kalori Makanan API Frontend..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ to build the frontend."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_error "Node.js version 18+ is required. Current version: $(node --version)"
    exit 1
fi

print_status "Node.js version: $(node --version) ✓"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed."
    exit 1
fi

# Navigate to frontend directory
FRONTEND_DIR="frontend"
if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found: $FRONTEND_DIR"
    exit 1
fi

print_status "Entering frontend directory..."
cd "$FRONTEND_DIR"

# Check if package.json exists
if [ ! -f "package.json" ]; then
    print_error "package.json not found in frontend directory"
    exit 1
fi

# Install dependencies
print_status "Installing npm dependencies..."
if npm ci --silent; then
    print_success "Dependencies installed successfully"
else
    print_warning "npm ci failed, trying npm install..."
    if npm install --silent; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Type check
print_status "Running TypeScript type check..."
if npm run type-check; then
    print_success "TypeScript type check passed"
else
    print_warning "TypeScript type check failed, but continuing with build..."
fi

# Build the React app
print_status "Building React application..."
if npm run build; then
    print_success "React app built successfully"
else
    print_error "Failed to build React app"
    exit 1
fi

# Check if build directory exists
if [ ! -d "dist" ]; then
    print_error "Build directory 'dist' not found after build"
    exit 1
fi

# Go back to root directory
cd ..

# Create static directory in FastAPI app
STATIC_DIR="app/static"
print_status "Creating static directory: $STATIC_DIR"
mkdir -p "$STATIC_DIR"

# Remove old static files
print_status "Cleaning old static files..."
rm -rf "$STATIC_DIR"/*

# Copy built files to static directory
print_status "Copying built files to static directory..."
if cp -r "$FRONTEND_DIR/dist/"* "$STATIC_DIR/"; then
    print_success "Files copied successfully"
else
    print_error "Failed to copy files to static directory"
    exit 1
fi

# Verify files were copied
if [ -f "$STATIC_DIR/index.html" ]; then
    print_success "index.html found in static directory"
else
    print_error "index.html not found in static directory"
    exit 1
fi

# Show build summary
echo ""
echo "📊 Build Summary:"
echo "=================="
echo "Frontend source: $FRONTEND_DIR/"
echo "Build output: $STATIC_DIR/"
echo "Files copied: $(find "$STATIC_DIR" -type f | wc -l)"
echo "Total size: $(du -sh "$STATIC_DIR" | cut -f1)"

print_success "🎉 Frontend build completed successfully!"
print_status "The React app will now be served at the root URL (/) by FastAPI"
print_status "API endpoints remain unchanged at /docs, /health, /foods, etc."

echo ""
echo "🚀 To start the server:"
echo "uvicorn app.main:app --host 0.0.0.0 --port 8000"
