#!/usr/bin/env python3
"""
Enpal Comprehensive API Server - Professionelle REST API für alle 97 FoxESS Parameter
Erweiterte API mit detailliertem Dashboard für Monitoring und Analyse
"""

import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

# Import des Comprehensive Data Fetchers
from enpal_comprehensive_data_fetcher import EnpalComprehensiveDataFetcher

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnpalComprehensiveAPIServer:
    """Comprehensive Flask API Server für alle FoxESS Parameter"""
    
    def __init__(self, host='0.0.0.0', port=5001):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        
        # CORS aktivieren
        CORS(self.app)
        
        # Comprehensive Data Fetcher initialisieren
        self.data_fetcher = EnpalComprehensiveDataFetcher()
        
        # Cached data für bessere Performance
        self.cached_data = {}
        self.last_update = None
        self.update_interval = 60  # Sekunden
        
        # Flask Routes registrieren
        self._register_routes()
        
        # Background Data Update
        self.update_thread = None
        self.running = False
        
        logger.info(f"Enpal Comprehensive API Server initialisiert - {host}:{port}")
    
    def _register_routes(self):
        """Registriert alle Flask-Routes"""
        
        @self.app.route('/')
        def comprehensive_dashboard():
            """Comprehensive Dashboard - Alle 97 FoxESS Parameter"""
            return render_template_string(self._get_comprehensive_dashboard_html())
        
        @self.app.route('/api/comprehensive')
        def api_comprehensive():
            """Alle 97 Parameter strukturiert"""
            try:
                if not self.cached_data:
                    self._update_data()
                
                return jsonify(self.cached_data)
                
            except Exception as e:
                logger.error(f"Fehler in /api/comprehensive: {e}")
                return jsonify({
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        @self.app.route('/api/power')
        def api_power():
            """Detaillierte Power-Daten"""
            try:
                power_data = self.data_fetcher.get_power_comprehensive()
                return jsonify({
                    'power': power_data,
                    'timestamp': datetime.now().isoformat(),
                    'total_fields': len(power_data)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/energy')
        def api_energy():
            """Detaillierte Energy-Daten"""
            try:
                energy_data = self.data_fetcher.get_energy_comprehensive()
                return jsonify({
                    'energy': energy_data,
                    'timestamp': datetime.now().isoformat(),
                    'total_fields': len(energy_data)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/battery')
        def api_battery():
            """Umfassende Batterie-Daten"""
            try:
                battery_data = self.data_fetcher.get_battery_comprehensive()
                return jsonify({
                    'battery': battery_data,
                    'timestamp': datetime.now().isoformat(),
                    'total_fields': len(battery_data)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/voltage')
        def api_voltage():
            """Spannungs-Daten"""
            try:
                voltage_data = self.data_fetcher.get_voltage_comprehensive()
                return jsonify({
                    'voltage': voltage_data,
                    'timestamp': datetime.now().isoformat(),
                    'total_fields': len(voltage_data)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/current')
        def api_current():
            """Strom-Daten"""
            try:
                current_data = self.data_fetcher.get_current_comprehensive()
                return jsonify({
                    'current': current_data,
                    'timestamp': datetime.now().isoformat(),
                    'total_fields': len(current_data)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/temperature')
        def api_temperature():
            """Temperatur-Daten"""
            try:
                temp_data = self.data_fetcher.get_temperature_comprehensive()
                return jsonify({
                    'temperature': temp_data,
                    'timestamp': datetime.now().isoformat(),
                    'total_fields': len(temp_data)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/raw')
        def api_raw():
            """Alle Rohdaten (97 Felder ungefiltert)"""
            try:
                raw_data = self.data_fetcher.get_all_raw_data()
                return jsonify({
                    'raw_data': raw_data,
                    'timestamp': datetime.now().isoformat(),
                    'total_fields': len(raw_data)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/export')
        def api_export():
            """JSON Export aller Daten"""
            try:
                # Temporären Export erstellen
                export_file = self.data_fetcher.export_to_json()
                
                with open(export_file, 'r', encoding='utf-8') as f:
                    export_data = json.load(f)
                
                return jsonify({
                    'export_file': export_file,
                    'data': export_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/status')
        def api_status():
            """System-Status"""
            return jsonify({
                'server': 'Enpal Comprehensive API Server',
                'version': '2.0.0',
                'raspberry_pi': '5',
                'python_version': '3.11.2',
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'update_interval': self.update_interval,
                'cached_data_available': bool(self.cached_data),
                'total_fields_captured': len(self.cached_data.get('raw_data', {})) if self.cached_data else 0,
                'influxdb_connection': self.data_fetcher.test_connection()
            })
    
    def _get_comprehensive_dashboard_html(self) -> str:
        """Generiert HTML für Comprehensive Dashboard"""
        return '''
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FoxESS Comprehensive Dashboard - Alle 97 Parameter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            background: #0d1117;
            color: #c9d1d9;
            line-height: 1.5;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .header h1 {
            color: #58a6ff;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .status-bar {
            display: flex;
            gap: 30px;
            font-size: 14px;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-online {
            color: #3fb950;
        }
        
        .status-offline {
            color: #f85149;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
        }
        
        .section {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .section h2 {
            color: #f0f6fc;
            font-size: 18px;
            margin-bottom: 15px;
            border-bottom: 1px solid #30363d;
            padding-bottom: 8px;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-table th {
            background: #21262d;
            color: #7d8590;
            text-align: left;
            padding: 8px 12px;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            border-bottom: 1px solid #30363d;
        }
        
        .data-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #21262d;
            font-size: 14px;
        }
        
        .data-table tr:hover {
            background: #21262d;
        }
        
        .field-name {
            color: #79c0ff;
            font-weight: 500;
        }
        
        .field-value {
            color: #a5f3fc;
            font-weight: 600;
        }
        
        .field-unit {
            color: #7d8590;
            font-size: 12px;
        }
        
        .overview {
            grid-column: 1 / -1;
            background: #0d1117;
            border: 2px solid #58a6ff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .overview h2 {
            color: #58a6ff;
            text-align: center;
            margin-bottom: 20px;
        }
        
        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .overview-item {
            text-align: center;
            padding: 15px;
            background: #161b22;
            border-radius: 6px;
            border: 1px solid #30363d;
        }
        
        .overview-value {
            font-size: 24px;
            font-weight: bold;
            color: #a5f3fc;
            margin-bottom: 5px;
        }
        
        .overview-label {
            font-size: 12px;
            color: #7d8590;
            text-transform: uppercase;
        }
        
        .api-links {
            background: #21262d;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
        }
        
        .api-links h3 {
            color: #f0f6fc;
            margin-bottom: 10px;
        }
        
        .api-links a {
            color: #58a6ff;
            text-decoration: none;
            margin-right: 15px;
            font-size: 14px;
        }
        
        .api-links a:hover {
            text-decoration: underline;
        }
        
        .loading {
            opacity: 0.6;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 0.6; }
            50% { opacity: 1; }
        }
        
        .error {
            background: #490202;
            border: 1px solid #f85149;
            color: #f85149;
            padding: 10px;
            border-radius: 6px;
            margin: 10px 0;
        }
        
        @media (max-width: 768px) {
            .grid {
                grid-template-columns: 1fr;
            }
            
            .overview-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            body {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔋 FoxESS Comprehensive Dashboard</h1>
            <div class="status-bar">
                <div class="status-item">
                    <span id="connectionStatus" class="status-offline">●</span>
                    <span id="connectionText">Verbinde...</span>
                </div>
                <div class="status-item">
                    <span>📍 Bonn-Beuel</span>
                </div>
                <div class="status-item">
                    <span id="fieldsCount">-- Felder</span>
                </div>
                <div class="status-item">
                    <span id="lastUpdate">Letzte Aktualisierung: --</span>
                </div>
            </div>
        </div>

        <div class="overview">
            <h2>⚡ Live System Overview</h2>
            <div class="overview-grid">
                <div class="overview-item">
                    <div class="overview-value" id="overviewPV">-- kW</div>
                    <div class="overview-label">PV-Produktion</div>
                </div>
                <div class="overview-item">
                    <div class="overview-value" id="overviewConsumption">-- kW</div>
                    <div class="overview-label">Hausverbrauch</div>
                </div>
                <div class="overview-item">
                    <div class="overview-value" id="overviewBattery">-- kW</div>
                    <div class="overview-label">Batterie</div>
                </div>
                <div class="overview-item">
                    <div class="overview-value" id="overviewGrid">-- kW</div>
                    <div class="overview-label">Netz</div>
                </div>
                <div class="overview-item">
                    <div class="overview-value" id="overviewSOC">--%</div>
                    <div class="overview-label">Batterie SOC</div>
                </div>
                <div class="overview-item">
                    <div class="overview-value" id="overviewToday">-- kWh</div>
                    <div class="overview-label">Heute produziert</div>
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="section">
                <h2>⚡ Power Data (21 Felder)</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Einheit</th>
                        </tr>
                    </thead>
                    <tbody id="powerTable">
                        <tr><td colspan="3" class="loading">Lade Power-Daten...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>🔋 Energy Data (23 Felder)</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Einheit</th>
                        </tr>
                    </thead>
                    <tbody id="energyTable">
                        <tr><td colspan="3" class="loading">Lade Energy-Daten...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>🔌 Voltage Data (9 Felder)</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Einheit</th>
                        </tr>
                    </thead>
                    <tbody id="voltageTable">
                        <tr><td colspan="3" class="loading">Lade Voltage-Daten...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>⚡ Current Data (6 Felder)</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Einheit</th>
                        </tr>
                    </thead>
                    <tbody id="currentTable">
                        <tr><td colspan="3" class="loading">Lade Current-Daten...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>🌡️ Temperature Data (2 Felder)</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Einheit</th>
                        </tr>
                    </thead>
                    <tbody id="temperatureTable">
                        <tr><td colspan="3" class="loading">Lade Temperature-Daten...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="section">
                <h2>🔋 Battery Comprehensive (16 Felder)</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Parameter</th>
                            <th>Wert</th>
                            <th>Einheit</th>
                        </tr>
                    </thead>
                    <tbody id="batteryTable">
                        <tr><td colspan="3" class="loading">Lade Battery-Daten...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="api-links">
            <h3>🔗 API Endpoints</h3>
            <a href="/api/comprehensive" target="_blank">Alle Daten</a>
            <a href="/api/power" target="_blank">Power</a>
            <a href="/api/energy" target="_blank">Energy</a>
            <a href="/api/battery" target="_blank">Battery</a>
            <a href="/api/voltage" target="_blank">Voltage</a>
            <a href="/api/current" target="_blank">Current</a>
            <a href="/api/temperature" target="_blank">Temperature</a>
            <a href="/api/raw" target="_blank">Raw Data</a>
            <a href="/api/export" target="_blank">JSON Export</a>
            <a href="/api/status" target="_blank">Status</a>
        </div>
    </div>

    <script>
        class ComprehensiveDashboard {
            constructor() {
                this.apiUrl = window.location.origin + '/api';
                this.updateInterval = 30000; // 30 Sekunden
                
                this.initDashboard();
            }
            
            async initDashboard() {
                console.log('🚀 Comprehensive Dashboard wird initialisiert...');
                await this.loadAllData();
                this.startAutoUpdate();
            }
            
            async loadAllData() {
                try {
                    this.setConnectionStatus('loading', 'Lade Daten...');
                    
                    // Alle API Endpoints parallel laden
                    const [power, energy, voltage, current, temperature, battery] = await Promise.all([
                        this.fetchData('/power'),
                        this.fetchData('/energy'),
                        this.fetchData('/voltage'),
                        this.fetchData('/current'),
                        this.fetchData('/temperature'),
                        this.fetchData('/battery')
                    ]);
                    
                    // Tabellen aktualisieren
                    this.updateTable('powerTable', power.power || {}, 'kW');
                    this.updateTable('energyTable', energy.energy || {}, 'kWh/Ah');
                    this.updateTable('voltageTable', voltage.voltage || {}, 'V');
                    this.updateTable('currentTable', current.current || {}, 'A');
                    this.updateTable('temperatureTable', temperature.temperature || {}, '°C');
                    this.updateTable('batteryTable', battery.battery || {}, 'mixed');
                    
                    // Overview aktualisieren
                    this.updateOverview(power.power || {}, energy.energy || {}, battery.battery || {});
                    
                    // Status aktualisieren
                    this.setConnectionStatus('online', 'System Online');
                    this.updateTimestamp();
                    
                    // Felder-Count
                    const totalFields = [power, energy, voltage, current, temperature, battery]
                        .reduce((sum, data) => sum + (data.total_fields || 0), 0);
                    document.getElementById('fieldsCount').textContent = `${totalFields} Felder erfasst`;
                    
                    console.log('✅ Alle Daten erfolgreich geladen');
                    
                } catch (error) {
                    console.error('❌ Fehler beim Laden der Daten:', error);
                    this.setConnectionStatus('offline', 'Verbindungsfehler');
                    this.showError('Fehler beim Laden der Comprehensive Daten: ' + error.message);
                }
            }
            
            async fetchData(endpoint) {
                const response = await fetch(`${this.apiUrl}${endpoint}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return await response.json();
            }
            
            updateTable(tableId, data, defaultUnit) {
                const tbody = document.getElementById(tableId);
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                for (const [key, value] of Object.entries(data)) {
                    const row = document.createElement('tr');
                    
                    // Parameter Name
                    const nameCell = document.createElement('td');
                    nameCell.innerHTML = `<span class="field-name">${this.formatFieldName(key)}</span>`;
                    
                    // Wert
                    const valueCell = document.createElement('td');
                    valueCell.innerHTML = `<span class="field-value">${this.formatValue(value)}</span>`;
                    
                    // Einheit
                    const unitCell = document.createElement('td');
                    unitCell.innerHTML = `<span class="field-unit">${this.getUnit(key, defaultUnit)}</span>`;
                    
                    row.appendChild(nameCell);
                    row.appendChild(valueCell);
                    row.appendChild(unitCell);
                    tbody.appendChild(row);
                }
            }
            
            updateOverview(power, energy, battery) {
                document.getElementById('overviewPV').textContent = 
                    `${power.production_total || 0} kW`;
                document.getElementById('overviewConsumption').textContent = 
                    `${power.consumption_total || 0} kW`;
                document.getElementById('overviewBattery').textContent = 
                    `${power.battery_charge_discharge || 0} kW`;
                document.getElementById('overviewGrid').textContent = 
                    `${power.external_total || 0} kW`;
                document.getElementById('overviewSOC').textContent = 
                    `${battery.soc_percent || 0}%`;
                document.getElementById('overviewToday').textContent = 
                    `${energy.production_total_day || 0} kWh`;
            }
            
            formatFieldName(key) {
                return key.replace(/_/g, ' ')
                         .replace(/\b\w/g, l => l.toUpperCase());
            }
            
            formatValue(value) {
                if (typeof value === 'number') {
                    return value.toLocaleString('de-DE', { 
                        minimumFractionDigits: 0, 
                        maximumFractionDigits: 3 
                    });
                }
                return value;
            }
            
            getUnit(key, defaultUnit) {
                if (key.includes('percent') || key.includes('soc') || key.includes('soh')) return '%';
                if (key.includes('voltage')) return 'V';
                if (key.includes('current')) return 'A';
                if (key.includes('temperature')) return '°C';
                if (key.includes('power') || key.includes('kw')) return 'kW';
                if (key.includes('energy') || key.includes('kwh')) return 'kWh';
                if (key.includes('ah')) return 'Ah';
                if (key.includes('lifetime')) return 'MWh';
                return defaultUnit;
            }
            
            setConnectionStatus(status, text) {
                const statusEl = document.getElementById('connectionStatus');
                const textEl = document.getElementById('connectionText');
                
                statusEl.className = `status-${status}`;
                textEl.textContent = text;
            }
            
            updateTimestamp() {
                const now = new Date().toLocaleString('de-DE');
                document.getElementById('lastUpdate').textContent = `Letzte Aktualisierung: ${now}`;
            }
            
            showError(message) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error';
                errorDiv.textContent = message;
                
                document.querySelector('.container').insertBefore(
                    errorDiv, 
                    document.querySelector('.grid')
                );
                
                setTimeout(() => errorDiv.remove(), 10000);
            }
            
            startAutoUpdate() {
                console.log(`🔄 Auto-Update gestartet (alle ${this.updateInterval/1000}s)`);
                
                setInterval(() => {
                    if (!document.hidden) {
                        this.loadAllData();
                    }
                }, this.updateInterval);
            }
        }
        
        // Dashboard initialisieren
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🎯 DOM geladen, starte Comprehensive Dashboard...');
            new ComprehensiveDashboard();
        });
    </script>
</body>
</html>
        '''
    
    def _update_data(self):
        """Aktualisiert die gecachten Daten"""
        try:
            logger.info("Aktualisiere comprehensive Dashboard-Daten...")
            
            # Alle Kategorien abrufen
            power_data = self.data_fetcher.get_power_comprehensive()
            energy_data = self.data_fetcher.get_energy_comprehensive()
            voltage_data = self.data_fetcher.get_voltage_comprehensive()
            current_data = self.data_fetcher.get_current_comprehensive()
            temperature_data = self.data_fetcher.get_temperature_comprehensive()
            battery_data = self.data_fetcher.get_battery_comprehensive()
            raw_data = self.data_fetcher.get_all_raw_data()
            
            self.cached_data = {
                'timestamp': datetime.now().isoformat(),
                'metadata': {
                    'total_fields_captured': len(raw_data),
                    'last_update': datetime.now().isoformat(),
                    'system_online': True
                },
                'power': power_data,
                'energy': energy_data,
                'voltage': voltage_data,
                'current': current_data,
                'temperature': temperature_data,
                'battery': battery_data,
                'raw_data': raw_data
            }
            
            self.last_update = datetime.now()
            logger.info("Comprehensive Dashboard-Daten erfolgreich aktualisiert")
            
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren der comprehensive Daten: {e}")
            self.cached_data = {
                'timestamp': datetime.now().isoformat(),
                'metadata': {'system_online': False, 'error': str(e)},
                'power': {}, 'energy': {}, 'voltage': {}, 'current': {},
                'temperature': {}, 'battery': {}, 'raw_data': {}
            }
    
    def _background_update(self):
        """Background-Thread für regelmäßige Daten-Updates"""
        logger.info(f"Background-Update gestartet (Intervall: {self.update_interval}s)")
        
        while self.running:
            try:
                self._update_data()
                time.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Fehler im Background-Update: {e}")
                time.sleep(10)
    
    def start_server(self, debug=False):
        """Startet den Flask-Server"""
        self.start_time = time.time()
        
        # Initial data load
        logger.info("Lade initiale comprehensive Daten...")
        self._update_data()
        
        # Background update thread starten
        self.running = True
        self.update_thread = threading.Thread(target=self._background_update, daemon=True)
        self.update_thread.start()
        
        logger.info(f"Starte Comprehensive Flask-Server auf http://{self.host}:{self.port}")
        
        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=debug,
                threaded=True
            )
        except KeyboardInterrupt:
            logger.info("Comprehensive Server wird beendet...")
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
    PORT = 5001       # Neuer Port für Comprehensive API
    DEBUG = False     # Produktionsmodus
    
    print("=== Enpal Comprehensive API Server - Raspberry Pi 5 ===")
    print(f"Startet auf: http://{HOST}:{PORT}")
    print("Verfügbare Endpoints:")
    print("  - / (Comprehensive Dashboard)")
    print("  - /api/comprehensive (Alle 97 Felder)")
    print("  - /api/power (21 Power-Felder)")
    print("  - /api/energy (23 Energy-Felder)")
    print("  - /api/battery (16 Battery-Felder)")
    print("  - /api/voltage (9 Voltage-Felder)")
    print("  - /api/current (6 Current-Felder)")
    print("  - /api/temperature (2 Temperature-Felder)")
    print("  - /api/raw (97 Rohdaten ungefiltert)")
    print("  - /api/export (JSON Export)")
    print("  - /api/status (Server-Status)")
    print("\nStrg+C zum Beenden")
    print("=" * 50)
    
    # Server erstellen und starten
    server = EnpalComprehensiveAPIServer(host=HOST, port=PORT)
    server.start_server(debug=DEBUG)