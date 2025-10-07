#!/bin/bash

# Installation script for Historical Facts MCP Server

echo "🚀 Installing Historical Facts MCP Server..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then 
    echo "✅ Python $PYTHON_VERSION detected (requires 3.10+)"
else
    echo "❌ Python 3.10+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔗 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "⬇️ Installing dependencies..."
pip install -r requirements.txt

# Test installation
echo "🧪 Testing installation..."
python test_api.py

if [ $? -eq 0 ]; then
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🎯 Next steps:"
    echo "1. For STDIO MCP mode:"
    echo "   python historical_facts_server.py"
    echo ""
    echo "2. For HTTP API mode:"
    echo "   python http_server.py"
    echo "   Then visit http://localhost:8000/docs"
    echo ""
    echo "3. For ChatGPT Desktop integration:"
    echo "   - Copy the path: $(pwd)/historical_facts_server.py"
    echo "   - Update claude_desktop_config.json with the correct path"
    echo "   - Add the configuration to your ChatGPT Desktop settings"
else
    echo "❌ Installation failed. Please check the error messages above."
    exit 1
fi
