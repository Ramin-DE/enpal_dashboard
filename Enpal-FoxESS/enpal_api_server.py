#!/usr/bin/env python3
"""
Enpal API Server - Flask Backend für Dashboard
Stellt REST API für Live-Daten bereit
"""

import json
import logging
import threading
import time
import os
from datetime import datetime
from typing import Dict, Any

from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_cors import CORS

# Import des Data Fetchers
from enpal_data_fetcher import EnpalDataFetcher

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnpalAPIServer:
    """Flask API Server für Enpal Dashboard"""
    
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        
        # CORS aktivieren für Cross-Origin Requests
        CORS(self.app)
        
        # Data Fetcher initialisieren
        self.data_fetcher = EnpalDataFetcher()
        
        # Cached data für bessere Performance
        self.cached_data = {}
        self.last_update = None
        self.update_interval = 60  # Sekunden
        
        # Flask Routes registrieren
        self._register_routes()
        
        # Background Data Update starten
        self.update_thread = None
        self.running = False
        
        logger.info(f"Enpal API Server initialisiert - {host}:{port}")
    
    def _register_routes(self):
        """Registriert alle Flask-Routes"""
        
        @self.app.route('/')
        def index():
            import os
            try:
                # Vollständiger Pfad zur index.html
                html_path = os.path.join(os.path.dirname(__file__), 'index.html')
                with open(html_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError:
                current_dir = os.getcwd()
                files = os.listdir('.')
                return f'''
                <h1>❌ index.html nicht gefunden</h1>
                <p><strong>Aktueller Pfad:</strong> {current_dir}</p>
                <p><strong>Verfügbare Dateien:</strong></p>
                <ul>{''.join([f"<li>{f}</li>" for f in files if f.endswith('.html') or f.endswith('.py')])}</ul>
                <p>Erstelle die index.html Datei im gleichen Verzeichnis wie enpal_api_server.py</p>
                '''
                
        @self.app.route('/api/data')
        def api_data():
            """Hauptendpoint - Alle Dashboard-Daten"""
            try:
                if not self.cached_data:
                    # Falls noch keine Cached-Daten, sofort abrufen
                    self._update_data()
                
                return jsonify(self.cached_data)
                
            except Exception as e:
                logger.error(f"Fehler in /api/data: {e}")
                return jsonify({
                    'error': str(e),
                    'status': {'online': False},
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/status')
        def api_status():
            """System-Status"""
            return jsonify({
                'server': 'Enpal API Server',
                'version': '1.0.0',
                'raspberry_pi': '5',
                'python_version': '3.11.2',
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'update_interval': self.update_interval,
                'cached_data_available': bool(self.cached_data),
                'influxdb_connection': self.data_fetcher.test_connection()
            })
        
        @self.app.route('/api/health')
        def api_health():
            """Health Check für Monitoring"""
            healthy = bool(self.cached_data and self.last_update)
            
            return jsonify({
                'healthy': healthy,
                'timestamp': datetime.now().isoformat(),
                'uptime_seconds': time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }), 200 if healthy else 503
        
        @self.app.route('/api/energy')
        def api_energy():
            """Nur Energiefluss-Daten"""
            try:
                energy_data = self.data_fetcher.get_energy_flow_data()
                return jsonify({
                    'energy_flow': energy_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/battery')
        def api_battery():
            """Nur Batterie-Daten"""
            try:
                battery_data = self.data_fetcher.get_battery_data()
                return jsonify({
                    'battery': battery_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def _update_data(self):
        """Aktualisiert die gecachten Daten"""
        try:
            logger.info("Aktualisiere Dashboard-Daten...")
            new_data = self.data_fetcher.get_complete_dashboard_data()
            
            if new_data and new_data.get('status', {}).get('online', False):
                self.cached_data = new_data
                self.last_update = datetime.now()
                logger.info("Dashboard-Daten erfolgreich aktualisiert")
            else:
                logger.warning("Fehlerhafte Daten empfangen - Cache nicht aktualisiert")
                
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der Daten: {e}")
    
    def _background_update(self):
        """Background-Thread für regelmäßige Daten-Updates"""
        logger.info(f"Background-Update gestartet (Intervall: {self.update_interval}s)")
        
        while self.running:
            try:
                self._update_data()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Fehler im Background-Update: {e}")
                time.sleep(10)  # Kurze Pause bei Fehlern
    
    def start_server(self, debug=False):
        """Startet den Flask-Server"""
        self.start_time = time.time()
        
        # Initial data load
        logger.info("Lade initiale Daten...")
        self._update_data()
        
        # Background update thread starten
        self.running = True
        self.update_thread = threading.Thread(target=self._background_update, daemon=True)
        self.update_thread.start()
        
        logger.info(f"Starte Flask-Server auf http://{self.host}:{self.port}")
        
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=debug,
                threaded=True
            )
        except KeyboardInterrupt:
            logger.info("Server wird beendet...")
        finally:
            self.running = False
    
    def stop_server(self):
        """Stoppt den Server"""
        self.running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)

if __name__ == "__main__":
    # Server-Konfiguration
    HOST = '0.0.0.0'  # Alle Netzwerk-Interfaces
    PORT = 5000       # Standard Flask Port
    DEBUG = False     # Produktionsmodus
    
    print("=== Enpal API Server - Raspberry Pi 5 ===")
    print(f"Startet auf: http://{HOST}:{PORT}")
    print("Verfügbare Endpoints:")
    print("  - / (Dashboard)")
    print("  - /api/data (Alle Daten)")
    print("  - /api/status (System-Status)")
    print("  - /api/health (Health Check)")
    print("  - /api/energy (Energiefluss)")
    print("  - /api/battery (Batterie)")
    print("\nStrg+C zum Beenden")
    print("=" * 40)
    
    # Server erstellen und starten
    server = EnpalAPIServer(host=HOST, port=PORT)
    server.start_server(debug=DEBUG)
