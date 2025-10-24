#!/usr/bin/env python3
"""
Enpal Comprehensive Data Fetcher - Vollständige FoxESS Integration
Erfasst ALLE 97 verfügbaren FoxESS Parameter strukturiert in Kategorien
Erweiterte Version für Monitoring, Analyse und Logging
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

class EnpalComprehensiveDataFetcher:
    """
    Comprehensive Data Fetcher für ALLE FoxESS Parameter
    Strukturierte Erfassung von 97 Feldern in logischen Kategorien
    """
    
    def __init__(self, config: Optional[InfluxConfig] = None):
        self.config = config or InfluxConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {self.config.token}',
            'Content-Type': 'application/vnd.flux',
            'Accept': 'application/csv'
        })
        logger.info(f"EnpalComprehensiveDataFetcher initialisiert für {self.config.base_url}")
    
    def _execute_flux_query(self, query: str) -> Optional[str]:
        """Führt Flux-Query gegen InfluxDB aus"""
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
        """Parst CSV-Response von InfluxDB zu Python-Dict - FÜR FOXESS FORMAT"""
        if not csv_data:
            return {}
        
        lines = [line.rstrip('\r') for line in csv_data.strip().split('\n') if line.strip()]
        result = {}
        current_field_names = []
        
        for line in lines:
            if not line or line.startswith('#'):
                continue
                
            parts = [p.strip() for p in line.split(',')]
            
            if line.startswith(',result,table,'):
                current_field_names = [name for name in parts[8:] if name]
                continue
                
            if line.startswith(',_result,') and current_field_names:
                values = parts[8:] if len(parts) > 8 else []
                
                for i, field_name in enumerate(current_field_names):
                    if i < len(values) and values[i] and field_name:
                        try:
                            value = values[i]
                            if value and value != 'None':
                                if '.' in value:
                                    result[field_name] = float(value)
                                else:
                                    result[field_name] = int(value)
                        except ValueError:
                            result[field_name] = values[i]
        
        logger.info(f"Parameter aus CSV geparst: {len(result)}")
        return result
    
    def get_all_raw_data(self) -> Dict[str, Any]:
        """Holt alle 97 verfügbaren Rohdaten"""
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
    
    def get_power_comprehensive(self) -> Dict[str, Any]:
        """Umfassende Leistungsdaten (21 Power-Felder)"""
        all_data = self.get_all_raw_data()
        
        return {
            'production_total': round(all_data.get('Power.Production.Total', 0) / 1000, 3),
            'consumption_total': round(all_data.get('Power.Consumption.Total', 0) / 1000, 3),
            'external_total': round(all_data.get('Power.External.Total', 0) / 1000, 3),
            'house_total': round(all_data.get('Power.House.Total', 0) / 1000, 3),
            'dc_string1': round(all_data.get('Power.DC.String.1', 0) / 1000, 3),
            'dc_string2': round(all_data.get('Power.DC.String.2', 0) / 1000, 3),
            'dc_total': round(all_data.get('Power.DC.Total', 0) / 1000, 3),
            'ac_phase_a': round(all_data.get('Power.AC.Phase.A', 0) / 1000, 3),
            'ac_phase_b': round(all_data.get('Power.AC.Phase.B', 0) / 1000, 3),
            'ac_phase_c': round(all_data.get('Power.AC.Phase.C', 0) / 1000, 3),
            'battery_charge_discharge': round(all_data.get('Power.Battery.Charge.Discharge', 0) / 1000, 3),
            'battery_charge_discharge_set': round(all_data.get('Power.Battery.Charge.Discharge.Set', 0) / 1000, 3),
            'battery_charge_max': round(all_data.get('Power.Battery.Charge.Max', 0) / 1000, 3),
            'battery_discharge_max': round(all_data.get('Power.Battery.Discharge.Max', 0) / 1000, 3),
            'storage_total': round(all_data.get('Power.Storage.Total', 0) / 1000, 3),
            'grid_export': round(all_data.get('Power.Grid.Export', 0) / 1000, 3),
            'power_factor': round(all_data.get('Power.Factor', 0), 3),
            'reactive_power': round(all_data.get('Power.Reactive', 0) / 1000, 3),
            'wallbox_charging': round(all_data.get('Power.Wallbox.Connector.1.Charging', 0) / 1000, 3),
            'wallbox_offered': round(all_data.get('Power.Wallbox.Connector.1.Offered', 0) / 1000, 3),
            'wallbox_requested': round(all_data.get('Power.Wallbox.Connector.1.Charging.Requested', 0) / 1000, 3)
        }
    
    def get_energy_comprehensive(self) -> Dict[str, Any]:
        """Umfassende Energiedaten (22 Energy-Felder)"""
        all_data = self.get_all_raw_data()
        
        return {
            'battery_ah': round(all_data.get('Energy.Battery.Ah', 0), 2),
            'battery_charge_level': round(all_data.get('Energy.Battery.Charge.Level', 0), 1),
            'battery_charge_level_absolute': round(all_data.get('Energy.Battery.Charge.Level.Absolute', 0), 1),
            'battery_charge_load': all_data.get('Energy.Battery.Charge.Load', 0),
            'storage_level': all_data.get('Energy.Storage.Level', 0),
            'percent_storage_level': round(all_data.get('Percent.Storage.Level', 0), 1),
            'battery_charge_day': round(all_data.get('Energy.Battery.Charge.Day', 0), 2),
            'battery_discharge_day': round(all_data.get('Energy.Battery.Discharge.Day', 0), 2),
            'consumption_total_day': round(all_data.get('Energy.Consumption.Total.Day', 0), 2),
            'production_total_day': round(all_data.get('Energy.Production.Total.Day', 0), 2),
            'grid_export_day': round(all_data.get('Energy.Grid.Export.Day', 0), 2),
            'grid_import_day': round(all_data.get('Energy.Grid.Import.Day', 0), 2),
            'external_total_in_day': round(all_data.get('Energy.External.Total.In.Day', 0), 2),
            'external_total_out_day': round(all_data.get('Energy.External.Total.Out.Day', 0), 2),
            'storage_total_in_day': round(all_data.get('Energy.Storage.Total.In.Day', 0), 2),
            'storage_total_out_day': round(all_data.get('Energy.Storage.Total.Out.Day', 0), 2),
            'battery_charge_lifetime': round(all_data.get('Energy.Battery.Charge.Lifetime', 0), 1),
            'battery_discharge_lifetime': round(all_data.get('Energy.Battery.Discharge.Lifetime', 0), 1),
            'consumption_total_lifetime': round(all_data.get('Energy.Consumption.Total.Lifetime', 0), 1),
            'production_total_lifetime': round(all_data.get('Energy.Production.Total.Lifetime', 0), 1),
            'grid_export_lifetime': round(all_data.get('Energy.Grid.Export.Lifetime', 0), 1),
            'grid_import_lifetime': round(all_data.get('Energy.Grid.Import.Lifetime', 0), 1),
            'wallbox_charged_total': round(all_data.get('Energy.Wallbox.Connector.1.Charged.Total', 0), 0)
        }
    
    def get_voltage_comprehensive(self) -> Dict[str, Any]:
        """Umfassende Spannungsdaten (9 Voltage-Felder)"""
        all_data = self.get_all_raw_data()
        
        return {
            'battery': round(all_data.get('Voltage.Battery', 0), 1),
            'phase_a': round(all_data.get('Voltage.Phase.A', 0), 1),
            'phase_b': round(all_data.get('Voltage.Phase.B', 0), 1),
            'phase_c': round(all_data.get('Voltage.Phase.C', 0), 1),
            'phase_average': round((all_data.get('Voltage.Phase.A', 0) + 
                                  all_data.get('Voltage.Phase.B', 0) + 
                                  all_data.get('Voltage.Phase.C', 0)) / 3, 1),
            'string1': round(all_data.get('Voltage.String.1', 0), 1),
            'string2': round(all_data.get('Voltage.String.2', 0), 1),
            'wallbox_phase_a': round(all_data.get('Voltage.Wallbox.Connector.1.Phase.A', 0), 1),
            'wallbox_phase_b': round(all_data.get('Voltage.Wallbox.Connector.1.Phase.B', 0), 1),
            'wallbox_phase_c': round(all_data.get('Voltage.Wallbox.Connector.1.Phase.C', 0), 1)
        }
    
    def get_current_comprehensive(self) -> Dict[str, Any]:
        """Umfassende Stromdaten (6 Current-Felder)"""
        all_data = self.get_all_raw_data()
        
        return {
            'battery': round(all_data.get('Current.Battery', 0), 2),
            'string1': round(all_data.get('Current.String.1', 0), 2),
            'string2': round(all_data.get('Current.String.2', 0), 2),
            'wallbox_phase_a': round(all_data.get('Current.Wallbox.Connector.1.Phase.A', 0), 2),
            'wallbox_phase_b': round(all_data.get('Current.Wallbox.Connector.1.Phase.B', 0), 2),
            'wallbox_phase_c': round(all_data.get('Current.Wallbox.Connector.1.Phase.C', 0), 2)
        }
    
    def get_temperature_comprehensive(self) -> Dict[str, Any]:
        """Umfassende Temperaturdaten (2 Temperature-Felder)"""
        all_data = self.get_all_raw_data()
        
        return {
            'battery': round(all_data.get('Temperature.Battery', 0), 1),
            'housing_inside': round(all_data.get('Temperature.Housing.Inside', 0), 1)
        }
    
    def get_battery_comprehensive(self) -> Dict[str, Any]:
        """Umfassende Batteriedaten (16 Battery-Felder + berechnete Werte)"""
        all_data = self.get_all_raw_data()
        
        soc = all_data.get('Energy.Battery.Charge.Level', 0)
        voltage = all_data.get('Voltage.Battery', 0)
        current = all_data.get('Current.Battery', 0)
        capacity_ah = all_data.get('Energy.Battery.Ah', 0)
        soh = all_data.get('Battery.SOH', 100)
        
        return {
            'soc_percent': round(soc, 1),
            'soh_percent': round(soh, 1),
            'charge_level_max': all_data.get('Battery.ChargeLevel.Max', 100),
            'charge_level_min': all_data.get('Battery.ChargeLevel.Min', 10),
            'charge_level_min_on_grid': all_data.get('Battery.ChargeLevel.MinOnGrid', 10),
            'voltage': round(voltage, 1),
            'current': round(current, 2),
            'capacity_ah': round(capacity_ah, 1),
            'power_kw': round(voltage * current / 1000, 3) if voltage and current else 0,
            'capacity_kwh': round(capacity_ah * voltage / 1000, 1) if capacity_ah and voltage else 0,
            'available_kwh': round(soc * capacity_ah * voltage / 100000, 1) if all([soc, capacity_ah, voltage]) else 0,
            'temperature': round(all_data.get('Temperature.Battery', 0), 1),
            'charged_today_kwh': round(all_data.get('Energy.Battery.Charge.Day', 0), 2),
            'discharged_today_kwh': round(all_data.get('Energy.Battery.Discharge.Day', 0), 2),
            'charged_lifetime_mwh': round(all_data.get('Energy.Battery.Charge.Lifetime', 0), 1),
            'discharged_lifetime_mwh': round(all_data.get('Energy.Battery.Discharge.Lifetime', 0), 1)
        }
    # Diese Funktionen müssen zu enpal_comprehensive_data_fetcher.py hinzugefügt werden:

    def export_to_json(self, filepath: str = None) -> str:
        """Exportiert alle Daten zu JSON-Datei"""
        # Alle Daten sammeln
        data = {
            'timestamp': datetime.now().isoformat(),
            'power': self.get_power_comprehensive(),
            'energy': self.get_energy_comprehensive(),
            'voltage': self.get_voltage_comprehensive(),
            'current': self.get_current_comprehensive(),
            'temperature': self.get_temperature_comprehensive(),
            'battery': self.get_battery_comprehensive(),
            'raw_data': self.get_all_raw_data()
        }
        
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"foxess_comprehensive_data_{timestamp}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Comprehensive Daten exportiert nach: {filepath}")
        return filepath    






    def test_connection(self) -> bool:
        """Testet Verbindung zur InfluxDB"""
        try:
            query = f'from(bucket:"{self.config.bucket}") |> range(start: -1m) |> limit(n:1)'
            result = self._execute_flux_query(query)
            return result is not None
        except Exception as e:
            logger.error(f"Verbindungstest-Fehler: {e}")
            return False

# Test-Funktion
if __name__ == "__main__":
    print("=== Enpal Comprehensive Data Fetcher - ALLE 97 FOXESS FELDER ===")
    
    fetcher = EnpalComprehensiveDataFetcher()
    
    if fetcher.test_connection():
        print("\n[POWER] Umfassende Leistungsdaten:")
        power_data = fetcher.get_power_comprehensive()
        for key, value in list(power_data.items())[:5]:
            print(f"  {key}: {value}")
        print(f"  ... (insgesamt {len(power_data)} Power-Felder)")
        
        print("\n[ENERGY] Umfassende Energiedaten:")
        energy_data = fetcher.get_energy_comprehensive()
        for key, value in list(energy_data.items())[:5]:
            print(f"  {key}: {value}")
        print(f"  ... (insgesamt {len(energy_data)} Energy-Felder)")
        
        print("\n[BATTERY] Umfassende Batteriedaten:")
        battery_data = fetcher.get_battery_comprehensive()
        for key, value in list(battery_data.items())[:8]:
            print(f"  {key}: {value}")
        
        print(f"\n=== SYSTEM OVERVIEW ===")
        print(f"PV-Produktion: {power_data.get('production_total', 0)} kW")
        print(f"Hausverbrauch: {power_data.get('consumption_total', 0)} kW")
        print(f"Batterie: {power_data.get('battery_charge_discharge', 0)} kW ({battery_data.get('soc_percent', 0)}%)")
        print(f"Netz: {power_data.get('external_total', 0)} kW")
        print(f"Heute produziert: {energy_data.get('production_total_day', 0)} kWh")
        
    else:
        print("[ERROR] Keine Verbindung zur InfluxDB möglich")