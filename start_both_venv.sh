#!/bin/bash
# Enpal Dashboard Starter mit Virtual Environment

cd /home/ramin/enpal_dashboard

echo "$(date): Starte Enpal API Server mit venv..."
/home/ramin/enpal_dashboard/venv/bin/python enpal_api_server.py &
API_PID=$!

echo "$(date): Starte Comprehensive API Server mit venv..."
/home/ramin/enpal_dashboard/venv/bin/python enpal_comprehensive_api_server.py &
COMP_PID=$!

echo "$(date): Server gestartet - API PID: $API_PID, Comprehensive PID: $COMP_PID"

# Warten bis beide Prozesse beendet sind
wait
