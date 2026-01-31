#!/bin/bash
# Find Kolibri server URL

echo "🔍 Finding Kolibri server..."
echo ""

# Check if kolibri command exists
if command -v kolibri &> /dev/null; then
    echo "✅ Kolibri is installed"
    
    # Check if Kolibri is running
    if kolibri status &> /dev/null; then
        echo "✅ Kolibri is running"
        
        # Try to get the URL from Kolibri config
        KOLIBRI_HOME="${KOLIBRI_HOME:-$HOME/.kolibri}"
        if [ -f "$KOLIBRI_HOME/server/port" ]; then
            PORT=$(cat "$KOLIBRI_HOME/server/port" 2>/dev/null)
            if [ -n "$PORT" ]; then
                echo ""
                echo "📍 Kolibri URL: http://localhost:$PORT"
                echo ""
                echo "Test it:"
                echo "  python scripts/kolibri-quick-test.py --kolibri-url http://localhost:$PORT"
                exit 0
            fi
        fi
        
        # Default port
        echo ""
        echo "📍 Default Kolibri URL: http://localhost:8080"
        echo ""
        echo "Test it:"
        echo "  python scripts/kolibri-quick-test.py --kolibri-url http://localhost:8080"
    else
        echo "❌ Kolibri is not running"
        echo ""
        echo "Start it with:"
        echo "  kolibri start"
    fi
else
    echo "❌ Kolibri command not found"
    echo ""
    echo "Install Kolibri:"
    echo "  pip install kolibri"
    echo "  # or"
    echo "  docker run -d -p 8080:8080 learningequality/kolibri"
fi

echo ""
echo "🔍 Checking common ports..."
for port in 8080 8000 3000 5000; do
    if curl -s "http://localhost:$port/api/content/channel" &> /dev/null; then
        echo "✅ Found server at http://localhost:$port"
        echo "   Test: python scripts/kolibri-quick-test.py --kolibri-url http://localhost:$port"
    fi
done
