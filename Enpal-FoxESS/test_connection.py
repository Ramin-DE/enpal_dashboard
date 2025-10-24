#!/usr/bin/env python3
"""
Basis-Test für InfluxDB Verbindung auf Raspberry Pi 5
"""

import requests
import sys
from datetime import datetime

# InfluxDB Konfiguration
INFLUX_CONFIG = {
    'host': '192.168.178.173',
    'port': 8086,
    'token': 'Ksi1d1Cg00vtnTPLS1PvvQUfn-TsDphAg7FaZYnbBV9Um9ogObp6afvtWthQnnhqTGMGOhOTyXYtEA37EJxzMA==',
    'org_id': 'bb63d87a19f7be18',
    'bucket': 'solar'
}

def test_influxdb_connection():
    """Teste InfluxDB Verbindung"""
    try:
        url = f"http://{INFLUX_CONFIG['host']}:{INFLUX_CONFIG['port']}/api/v2/query"
        headers = {
            'Authorization': f"Token {INFLUX_CONFIG['token']}",
            'Content-Type': 'application/vnd.flux',
            'Accept': 'application/csv'
        }
        
        # Einfache Test-Query
        query = f'''
        from(bucket:"{INFLUX_CONFIG['bucket']}") 
          |> range(start: -5m) 
          |> limit(n:1)
        '''
        
        params = {'org': INFLUX_CONFIG['org_id']}
        
        print(f"[TEST] Teste Verbindung zu {INFLUX_CONFIG['host']}:{INFLUX_CONFIG['port']}")
        
        response = requests.post(url, headers=headers, params=params, data=query, timeout=10)
        
        if response.status_code == 200:
            print("[SUCCESS] InfluxDB Verbindung erfolgreich!")
            print(f"[DATA] Datenumfang: {len(response.text)} Zeichen")
            
            # Zeige erste Zeilen der Antwort
            lines = response.text.split('\n')[:5]
            print("[INFO] Erste Datenzeilen:")
            for line in lines:
                if line.strip():
                    print(f"   {line}")
            
            return True
        else:
            print(f"[ERROR] HTTP Fehler: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("[ERROR] Verbindungsfehler - InfluxDB nicht erreichbar")
        return False
    except requests.exceptions.Timeout:
        print("[ERROR] Timeout - InfluxDB antwortet nicht")
        return False
    except Exception as e:
        print(f"[ERROR] Unerwarteter Fehler: {e}")
        return False

def test_system_info():
    """Zeige System-Informationen"""
    import platform
    import socket
    
    print("\n[SYSTEM] System-Informationen:")
    print(f"   Python: {platform.python_version()}")
    print(f"   System: {platform.system()} {platform.release()}")
    print(f"   Hostname: {socket.gethostname()}")
    
    # IP-Adresse ermitteln
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        print(f"   Lokale IP: {local_ip}")
    except:
        print("   Lokale IP: Nicht ermittelbar")

if __name__ == "__main__":
    print("=== Enpal Dashboard - Raspberry Pi 5 Connection Test ===")
    print(f"Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_system_info()
    print()
    
    if test_influxdb_connection():
        print("\n[SUCCESS] Basis-Test erfolgreich! Weiter mit Projekt-Setup.")
        sys.exit(0)
    else:
        print("\n[FAILED] Basis-Test fehlgeschlagen! Überprüfe Netzwerk und InfluxDB.")
        sys.exit(1)