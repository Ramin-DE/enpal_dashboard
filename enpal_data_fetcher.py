#!/usr/bin/env python3
"""
Enpal Data Fetcher - InfluxDB Integration (FINALE VERSION MIT ECHTEN FOXESS FELDNAMEN)
Holt alle FoxESS Parameter aus der InfluxDB und bereitet sie für das Dashboard auf
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from dataclasses import dataclass

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class InfluxConfig:
    """Konfiguration für InfluxDB-Verbindung"""
    host: str = "192.168.178.173"
    port: int = 8086
    token: str = "Ksi1d1Cg00vtnTPLS1PvvQUfn-TsDphAg7FaZYnbBV9Um9ogObp6afvtWthQnnhqTGMGOhOTyXYtEA37EJxzMA=="
    org_id: str = "bb63d87a19f7be18"
    bucket: str = "solar"
    
    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

class EnpalDataFetcher:
    """
    Hauptklasse für Datenabruf aus InfluxDB
    Konvertiert Flux-Queries zu strukturierten Python-Daten
    """
    
    def __init__(self, config: Optional[InfluxConfig] = None):
        self.config = config or InfluxConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {self.config.token}',
            'Content-Type': 'application/vnd.flux',
            'Accept': 'application/csv'
        })
        logger.info(f"EnpalDataFetcher initialisiert für {self.config.base_url}")
    
    def _execute_flux_query(self, query: str) -> Optional[str]:
        """
        Führt Flux-Query gegen InfluxDB aus
        
        Args:
            query: Flux-Query String
            
        Returns:
            CSV-Response als String oder None bei Fehler
        """
        try:
            url = f"{self.config.base_url}/api/v2/query"
            params = {'org': self.config.org_id}
            
            logger.debug(f"Ausführung Flux-Query: {query[:100]}...")
            response = self.session.post(url, params=params, data=query, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Query erfolgreich ausgeführt ({len(response.text)} Zeichen)")
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"InfluxDB Query-Fehler: {e}")
            return None
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")
            return None
    
    def _parse_csv_response(self, csv_data: str) -> Dict[str, Any]:
        """
        Parst CSV-Response von InfluxDB zu Python-Dict - FÜR FOXESS FORMAT
        
        Args:
            csv_data: CSV-String von InfluxDB
            
        Returns:
            Dictionary mit Feldnamen als Keys und Werten
        """
        if not csv_data:
            return {}
        
        # Zeilen aufteilen und \r entfernen
        lines = [line.rstrip('\r') for line in csv_data.strip().split('\n') if line.strip()]
        
        result = {}
        current_field_names = []
        
        for line in lines:
            if not line or line.startswith('#'):
                continue
                
            parts = [p.strip() for p in line.split(',')]
            
            # Header-Zeile erkennen (enthält result,table,_start...)
            if line.startswith(',result,table,'):
                # Feldnamen aus Header extrahieren (ab Index 8)
                current_field_names = [name for name in parts[8:] if name]
                logger.debug(f"Feldnamen gefunden: {current_field_names}")
                continue
                
            # Daten-Zeile (beginnt mit ,_result,)
            if line.startswith(',_result,') and current_field_names:
                # Werte ab Index 8 extrahieren
                values = parts[8:] if len(parts) > 8 else []
                
                # Feldnamen mit Werten verknüpfen
                for i, field_name in enumerate(current_field_names):
                    if i < len(values) and values[i] and field_name:
                        try:
                            # Numerische Konvertierung
                            value = values[i]
                            if value and value != 'None':
                                if '.' in value:
                                    result[field_name] = float(value)
                                else:
                                    result[field_name] = int(value)
                        except ValueError:
                            result[field_name] = values[i]  # Als String belassen
        
        logger.info(f"Parameter aus CSV geparst: {len(result)}")
        
        # Debug: Zeige erste paar Werte
        if result:
            sample = dict(list(result.items())[:5])
            logger.debug(f"Sample Daten: {sample}")
        else:
            logger.warning("Keine Daten geparst!")
            logger.debug(f"Erste 3 Zeilen: {lines[:3]}")
        
        return result
    
    def get_latest_all_data(self) -> Dict[str, Any]:
        """
        Holt alle verfügbaren aktuellen Daten
        
        Returns:
            Dictionary mit allen aktuellen Systemwerten
        """
        query = f'''
        from(bucket:"{self.config.bucket}") 
          |> range(start: -5m) 
          |> last()
          |> pivot(rowKey:["_time"], columnKey:["_field"], valueColumn:"_value")
        '''
        
        csv_response = self._execute_flux_query(query)
        if csv_response:
            return self._parse_csv_response(csv_response)
        return {}
    
    def get_energy_flow_data(self) -> Dict[str, float]:
        """
        Holt spezifische Daten für Energiefluss-Anzeige - MIT ECHTEN FOXESS FELDNAMEN
        
        Returns:
            Dictionary mit Leistungswerten in kW
        """
        all_data = self.get_latest_all_data()
        
        # Echte FoxESS Feldnamen verwenden
        pv_power = all_data.get('Power.Production.Total', 0) / 1000  # W zu kW
        consumption_power = all_data.get('Power.Consumption.Total', 0) / 1000
        battery_power = all_data.get('Power.Battery.Charge.Discharge', 0) / 1000
        grid_power = all_data.get('Power.External.Total', 0) / 1000
        
        return {
            'pv_power': round(pv_power, 2),
            'consumption_power': round(consumption_power, 2),
            'battery_power': round(battery_power, 2),
            'grid_power': round(grid_power, 2)
        }
    
    def get_battery_data(self) -> Dict[str, Any]:
        """
        Holt Batterie-spezifische Daten - MIT ECHTEN FOXESS FELDNAMEN
        
        Returns:
            Dictionary mit Batterie-Status
        """
        all_data = self.get_latest_all_data()
        
        # Echte FoxESS Batterie-Feldnamen
        soc = all_data.get('Energy.Battery.Charge.Level', 0)
        temperature = all_data.get('Temperature.Battery', 20)
        voltage = all_data.get('Voltage.Battery', 0)
        current = all_data.get('Current.Battery', 0)
        capacity_ah = all_data.get('Energy.Battery.Ah', 0)
        soh = all_data.get('Battery.SOH', 100)
        
        return {
            'soc': round(soc, 1),
            'temperature': round(temperature, 1),
            'voltage': round(voltage, 1),
            'current': round(current, 1),
            'capacity_ah': round(capacity_ah, 1),
            'health': round(soh, 1)
        }
    
    def get_string_data(self) -> Dict[str, Any]:
        """
        Holt String-spezifische Daten für Balance-Monitoring - MIT ECHTEN FOXESS FELDNAMEN
        
        Returns:
            Dictionary mit String-Performance
        """
        all_data = self.get_latest_all_data()
        
        # Echte FoxESS String-Feldnamen
        string1_power = all_data.get('Power.DC.String.1', 0) / 1000  # W zu kW
        string2_power = all_data.get('Power.DC.String.2', 0) / 1000
        string1_voltage = all_data.get('Voltage.String.1', 0)
        string2_voltage = all_data.get('Voltage.String.2', 0)
        string1_current = all_data.get('Current.String.1', 0)
        string2_current = all_data.get('Current.String.2', 0)
        
        # Balance berechnen (Prozentuale Abweichung)
        if string1_power > 0 and string2_power > 0:
            balance = round(min(string1_power, string2_power) / max(string1_power, string2_power) * 100, 1)
        else:
            balance = 100
        
        return {
            'string1_power': round(string1_power, 2),
            'string2_power': round(string2_power, 2),
            'string1_voltage': round(string1_voltage, 1),
            'string2_voltage': round(string2_voltage, 1),
            'string1_current': round(string1_current, 1),
            'string2_current': round(string2_current, 1),
            'balance_percentage': balance
        }
    
    def get_system_health_data(self) -> Dict[str, Any]:
        """
        Holt System-Health Daten - MIT ECHTEN FOXESS FELDNAMEN
        
        Returns:
            Dictionary mit System-Status
        """
        all_data = self.get_latest_all_data()
        
        # Echte FoxESS System-Feldnamen
        inverter_temp = all_data.get('Temperature.Housing.Inside', 0)
        grid_frequency = all_data.get('Frequency.Grid', 50.0)
        # Durchschnittsspannung der 3 Phasen berechnen
        voltage_a = all_data.get('Voltage.Phase.A', 230)
        voltage_b = all_data.get('Voltage.Phase.B', 230) 
        voltage_c = all_data.get('Voltage.Phase.C', 230)
        grid_voltage = (voltage_a + voltage_b + voltage_c) / 3
        
        # CPU Load und Memory Usage
        cpu_load = all_data.get('Cpu.Load', 0)
        memory_usage = all_data.get('Memory.Usage', 0)
        
        return {
            'inverter_temp': round(inverter_temp, 1),
            'grid_frequency': round(grid_frequency, 2),
            'grid_voltage': round(grid_voltage, 1),
            'cpu_load': round(cpu_load, 1),
            'memory_usage': round(memory_usage, 1),
            'system_uptime': 0  # Nicht verfügbar in FoxESS
        }
    
    def get_daily_summary(self) -> Dict[str, float]:
        """
        Holt Tageszusammenfassung - MIT ECHTEN FOXESS DAILY FELDNAMEN
        
        Returns:
            Dictionary mit Tageswerten in kWh
        """
        all_data = self.get_latest_all_data()
        
        # Echte FoxESS Daily-Feldnamen (bereits in kWh!)
        production_day = all_data.get('Energy.Production.Total.Day', 0)  # Bereits in kWh
        consumption_day = all_data.get('Energy.Consumption.Total.Day', 0)  # Bereits in kWh
        export_day = all_data.get('Energy.Grid.Export.Day', 0)  # Bereits in kWh
        import_day = all_data.get('Energy.Grid.Import.Day', 0)  # Bereits in kWh
        
        # Netto Grid-Power (Export - Import)
        grid_export_day = export_day - import_day
        
        # Autarkiegrad berechnen
        if consumption_day > 0:
            # Eigenverbrauch = Produktion - Export
            self_consumption = production_day - export_day
            autarky = min(100, round(self_consumption / consumption_day * 100, 1))
        else:
            autarky = 0
        
        result = {
            'production_today': round(production_day, 2),
            'consumption_today': round(consumption_day, 2),
            'grid_export_today': round(max(0, grid_export_day), 2),  # Nur positive Werte
            'autarky_rate': max(0, autarky)
        }
        
        logger.info(f"Daily Summary (FoxESS): {result}")
        return result
    
    def get_complete_dashboard_data(self) -> Dict[str, Any]:
        """
        Holt alle Dashboard-Daten in einem strukturierten Format
        
        Returns:
            Vollständiges Dashboard-Datenset
        """
        logger.info("Hole vollständige Dashboard-Daten...")
        
        try:
            # Alle Datengruppen abrufen
            energy_flow = self.get_energy_flow_data()
            battery = self.get_battery_data()
            strings = self.get_string_data()
            system = self.get_system_health_data()
            daily = self.get_daily_summary()
            
            # Timestamp und Status
            timestamp = datetime.now().isoformat()
            data_age = 60  # Placeholder
            
            dashboard_data = {
                'timestamp': timestamp,
                'status': {
                    'online': True,
                    'data_age_seconds': data_age,
                    'last_update': timestamp
                },
                'energy_flow': energy_flow,
                'battery': battery,
                'strings': strings,
                'system': system,
                'daily': daily,
                'calculated': {
                    'total_string_power': round(strings['string1_power'] + strings['string2_power'], 2),
                    'string_balance': strings['balance_percentage'],
                    'battery_capacity_kwh': round(battery['capacity_ah'] * battery['voltage'] / 1000, 1) if battery['voltage'] > 0 else 12.4
                }
            }
            
            logger.info("Dashboard-Daten erfolgreich zusammengestellt")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Fehler beim Zusammenstellen der Dashboard-Daten: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'status': {'online': False, 'error': str(e)},
                'energy_flow': {},
                'battery': {},
                'strings': {},
                'system': {},
                'daily': {},
                'calculated': {}
            }
    
    def test_connection(self) -> bool:
        """
        Testet Verbindung zur InfluxDB
        
        Returns:
            True wenn Verbindung erfolgreich
        """
        try:
            query = f'from(bucket:"{self.config.bucket}") |> range(start: -1m) |> limit(n:1)'
            result = self._execute_flux_query(query)
            success = result is not None
            
            if success:
                logger.info("InfluxDB-Verbindung erfolgreich getestet")
            else:
                logger.error("InfluxDB-Verbindungstest fehlgeschlagen")
                
            return success
            
        except Exception as e:
            logger.error(f"Verbindungstest-Fehler: {e}")
            return False

# Test-Funktion
if __name__ == "__main__":
    print("=== Teste EnpalDataFetcher (FINALE VERSION MIT FOXESS FELDNAMEN) ===")
    
    fetcher = EnpalDataFetcher()
    
    # Verbindung testen
    if fetcher.test_connection():
        print("\n[ENERGY] Energiefluss-Daten (Live FoxESS):")
        energy_data = fetcher.get_energy_flow_data()
        for key, value in energy_data.items():
            print(f"  {key}: {value}")
        
        print("\n[BATTERY] Batterie-Daten (Live FoxESS):")
        battery_data = fetcher.get_battery_data()
        for key, value in battery_data.items():
            print(f"  {key}: {value}")
        
        print("\n[STRINGS] String-Performance (Live FoxESS):")
        string_data = fetcher.get_string_data()
        for key, value in string_data.items():
            print(f"  {key}: {value}")
        
        print("\n[SYSTEM] System-Health (Live FoxESS):")
        system_data = fetcher.get_system_health_data()
        for key, value in system_data.items():
            print(f"  {key}: {value}")
        
        print("\n[DAILY] Tageszusammenfassung (Live FoxESS):")
        daily_data = fetcher.get_daily_summary()
        for key, value in daily_data.items():
            print(f"  {key}: {value}")
        
        print("\n[COMPLETE] Vollständige Dashboard-Daten:")
        complete_data = fetcher.get_complete_dashboard_data()
        print(f"  Datengruppen: {list(complete_data.keys())}")
        print(f"  Status: {complete_data['status']}")
        
        print(f"\n=== LIVE SYSTEM STATUS ===")
        print(f"PV-Produktion: {energy_data['pv_power']} kW")
        print(f"Hausverbrauch: {energy_data['consumption_power']} kW")
        print(f"Batterie: {energy_data['battery_power']} kW ({battery_data['soc']}%)")
        print(f"Netz: {energy_data['grid_power']} kW")
        print(f"Heute produziert: {daily_data['production_today']} kWh")
        print(f"String Balance: {string_data['balance_percentage']}%")
        
    else:
        print("[ERROR] Keine Verbindung zur InfluxDB möglich")