#!/bin/bash

# FPL Optimizer - Cron Job Setup Script
# This script sets up automated weekly optimization

echo "================================"
echo "FPL Optimizer - Cron Job Setup"
echo "================================"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Project directory: $PROJECT_DIR"
echo ""

# Check if virtual environment exists
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    cd "$PROJECT_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    echo "✓ Virtual environment created and dependencies installed"
else
    echo "✓ Virtual environment found"
fi

# Create the cron job script
CRON_SCRIPT="$PROJECT_DIR/run_weekly_optimization.sh"

cat > "$CRON_SCRIPT" << 'EOF'
#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Change to project directory
cd "$SCRIPT_DIR"

# Run optimization with weighted average method (best performing)
python examples/weekly_automation.py --method weighted_average

# Optionally, send email notification
# mail -s "FPL Weekly Optimization Complete" your@email.com < data/gameweek_results.json

# Deactivate virtual environment
deactivate
EOF

chmod +x "$CRON_SCRIPT"

echo "✓ Created cron job script: $CRON_SCRIPT"
echo ""

# Show cron job instructions
echo "To schedule this to run automatically:"
echo ""
echo "1. Open your crontab:"
echo "   crontab -e"
echo ""
echo "2. Add one of these lines:"
echo ""
echo "   # Run every Friday at 10 AM (before deadline)"
echo "   0 10 * * 5 $CRON_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1"
echo ""
echo "   # Run every Friday at 10 AM AND Tuesday at 10 AM (for double gameweeks)"
echo "   0 10 * * 2,5 $CRON_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1"
echo ""
echo "   # Test run: Every day at 9 AM"
echo "   0 9 * * * $CRON_SCRIPT >> $PROJECT_DIR/logs/cron.log 2>&1"
echo ""
echo "3. Save and exit"
echo ""

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"
echo "✓ Created logs directory: $PROJECT_DIR/logs"
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To test the script manually:"
echo "  $CRON_SCRIPT"
echo ""
