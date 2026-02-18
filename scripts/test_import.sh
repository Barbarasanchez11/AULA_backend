#!/bin/bash

# Test script for CSV import
# This script helps test the import functionality

echo "============================================================"
echo "AULA+ CSV Import Test"
echo "============================================================"
echo ""

# Check if CSV file is provided
if [ -z "$1" ]; then
    echo "Usage: ./test_import.sh <csv_file>"
    echo "Example: ./test_import.sh scripts/example_events.csv"
    exit 1
fi

CSV_FILE=$1

# Check if file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "❌ Error: CSV file not found: $CSV_FILE"
    exit 1
fi

echo "📄 CSV file: $CSV_FILE"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not activated"
    echo "   Activate it with: source venv/bin/activate"
    echo ""
fi

# Check if database is accessible
echo "🔍 Checking database connection..."
python3 -c "
import sys
sys.path.insert(0, '.')
from app.config import settings
print(f'   Database URL: {settings.database_url[:50]}...')
" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Error: Could not load database configuration"
    echo "   Make sure .env file exists and is configured"
    exit 1
fi

echo "✅ Database configuration loaded"
echo ""

# Run the import
echo "🚀 Starting import..."
echo ""

python3 scripts/import_events_from_csv.py "$CSV_FILE"

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Import completed successfully"
else
    echo "❌ Import failed with exit code: $EXIT_CODE"
fi

exit $EXIT_CODE



