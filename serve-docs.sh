#!/bin/bash
# Simple script to serve documentation with stable settings

echo "🚀 Starting Azure AI Search Handbook Documentation"
echo "=================================================="

# Check if mkdocs.yml exists
if [ ! -f "mkdocs.yml" ]; then
    echo "❌ mkdocs.yml not found!"
    echo "💡 Make sure you're in the project root directory"
    exit 1
fi

# Find available port
PORT=8000
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done

echo "🌐 Starting server at http://localhost:$PORT"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Start MkDocs with stable settings
mkdocs serve --dev-addr localhost:$PORT --no-livereload