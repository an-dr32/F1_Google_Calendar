#!/bin/bash

echo "🚀 Setting up virtual environment..."

# Create and activate venv
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Environment ready. To activate later, run:"
echo "   source venv/bin/activate # To activate the virtual environment"
echo "   To deactivate, just run 'deactivate'."
echo "💡 Remember to activate the virtual environment before running the app!"
echo "🎉 Setup complete!"
