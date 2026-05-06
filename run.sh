#!/bin/bash

# Wildlife Intelligence Command Center - Launch Script

echo "🚀 Starting Wildlife Intelligence Command Center..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "✓ Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found!"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

echo "✓ Virtual environment activated"
echo "✓ Starting Streamlit application..."
echo ""
echo "📊 Dashboard will open in your browser at: http://localhost:8501"
echo ""

# Run the application
streamlit run app.py
