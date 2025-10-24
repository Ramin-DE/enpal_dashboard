# Zuerst alle 97 Felder anzeigen um die richtigen Namen zu finden
from enpal_data_fetcher import EnpalDataFetcher

fetcher = EnpalDataFetcher()
all_data = fetcher.get_latest_all_data()

print("=== ALLE 97 VERFÜGBARE FOXESS FELDER ===")
for field in sorted(all_data.keys()):
    print(f"{field}: {all_data[field]}")

print("\n=== POWER FELDER (Leistung) ===")
power_fields = {k: v for k, v in all_data.items() if 'power' in k.lower()}
for field, value in power_fields.items():
    print(f"{field}: {value}")

print("\n=== ENERGY FELDER (Energie) ===") 
energy_fields = {k: v for k, v in all_data.items() if 'energy' in k.lower()}
for field, value in energy_fields.items():
    print(f"{field}: {value}")

print("\n=== VOLTAGE FELDER (Spannung) ===")
voltage_fields = {k: v for k, v in all_data.items() if 'voltage' in k.lower()}
for field, value in voltage_fields.items():
    print(f"{field}: {value}")

print("\n=== CURRENT FELDER (Strom) ===")
current_fields = {k: v for k, v in all_data.items() if 'current' in k.lower()}
for field, value in current_fields.items():
    print(f"{field}: {value}")

print("\n=== TEMPERATURE FELDER ===")
temp_fields = {k: v for k, v in all_data.items() if 'temperature' in k.lower()}
for field, value in temp_fields.items():
    print(f"{field}: {value}")