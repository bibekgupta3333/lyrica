#!/bin/bash

# Lyrica Backend Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up Lyrica Backend..."

# Check Python version
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 is required but not installed"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3.12 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data/chromadb

# Generate secret key
echo "🔐 Generating secret key..."
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s/your-secret-key-here-change-in-production/${SECRET_KEY}/g" .env
else
    # Linux
    sed -i "s/your-secret-key-here-change-in-production/${SECRET_KEY}/g" .env
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Update .env with your configuration"
echo "  3. Install Ollama: curl -fsSL https://ollama.ai/install.sh | sh"
echo "  4. Pull Ollama model: ollama pull llama3"
echo "  5. Start services: docker-compose up -d postgres redis chromadb"
echo "  6. Run application: python app/main.py"
echo ""
echo "📚 API Documentation will be available at: http://localhost:8000/docs"

