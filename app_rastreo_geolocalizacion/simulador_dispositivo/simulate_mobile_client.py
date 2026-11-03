#!/usr/bin/env python3
"""
Simulador de Cliente Móvil GPS con Telemetría Periódica y Pruebas de Anomalías
Taller No. 2 - Mecanismos de Seguridad Informática
Universidad Distrital Francisco José de Caldas - 2026
"""

import time
import requests
import sys

API_URL = "http://127.0.0.1:8000/api/v1"
DEVICE_ID = "DEV-573108892341"
AUTH_TOKEN = "token_laboratorio_sec_2026"

# Ruta de prueba realista por Bogotá (Inicia en UD Sede Calle 40 y se desplaza al Parque Nacional)
WAYPOINTS = [
    # Paso 1 a 3: Dentro de la Geocerca de la UD (Zona Segura)
    {"lat": 4.628031, "lon": -74.065120, "speed": 0.0, "battery": 98.0, "desc": "Campus UD Calle 40 (Estático - Biblioteca)"},
    {"lat": 4.628400, "lon": -74.064800, "speed": 4.5, "battery": 97.5, "desc": "Campus UD (Salida peatonal Cra 7)"},
    {"lat": 4.629100, "lon": -74.064200, "speed": 12.0, "battery": 97.0, "desc": "Cra 7 con Calle 40 (Límite perímetro geocerca)"},
    
    # Paso 4 a 6: Salida de Geocerca (Dispara alerta GEOFENCE_EXIT)
    {"lat": 4.632000, "lon": -74.062500, "speed": 28.5, "battery": 96.0, "desc": "Cra 7 con Calle 43 (FUERA DE GEOCERCA)"},
    {"lat": 4.635000, "lon": -74.060500, "speed": 34.0, "battery": 95.0, "desc": "Cra 7 con Calle 45 (Hacia Parque Nacional)"},
    {"lat": 4.637012, "lon": -74.059044, "speed": 38.0, "battery": 94.5, "desc": "Parque Nacional / Javeriana (Alerta confirmada)"},
    
    # Paso 7: Salto Imposible Cinemático (Simula Spoofing / Teletransportación GPS)
    {"lat": 4.710989, "lon": -74.072092, "speed": 450.0, "battery": 93.0, "desc": "SIMULACIÓN SPOOFING: Salto instantáneo a Calle 127 (>10 km en 3s)"}
]

def run_simulation():
    print("================================================================================")
    print("      SIMULADOR DE TELEMETRÍA MÓVIL Y PRUEBA DE GEOFENCING / IA                 ")
    print("================================================================================")
    print(f"[*] Conectando con API Backend: {API_URL}")
    print(f"[*] Dispositivo simulado: {DEVICE_ID}")
    
    # Verificar salud del backend
    try:
        r = requests.get(f"{API_URL}/devices", timeout=3)
        if r.status_code != 200:
            print(f"[!] Error al contactar backend: {r.status_code}")
            return
    except Exception as e:
        print(f"[!] No se puede conectar a {API_URL}. Inicie primero el servidor FastAPI con:")
        print("    python -m uvicorn main:app --reload")
        return

    print("[+] Servidor detectado en línea. Transmitiendo telemetría en tiempo real...\n")
    
    for i, pt in enumerate(WAYPOINTS, start=1):
        payload = {
            "device_id": DEVICE_ID,
            "token": AUTH_TOKEN,
            "latitude": pt["lat"],
            "longitude": pt["lon"],
            "accuracy": 4.0,
            "speed": pt["speed"],
            "battery_level": pt["battery"]
        }
        
        print(f"[{i}/{len(WAYPOINTS)}] Enviando reporte: ({pt['lat']:.6f}, {pt['lon']:.6f}) - {pt['desc']}")
        try:
            resp = requests.post(f"{API_URL}/location/report", json=payload, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                geo_st = data.get("geofence_status")
                ml_info = data.get("kinematic_analysis", {})
                alerts = data.get("alerts_triggered", [])
                
                print(f"      -> Geocerca: {geo_st} | Dist: {data.get('geofence_details', {}).get('distance_m')} m")
                print(f"      -> Cinemática: {ml_info.get('speed_kmh')} km/h | Anomaly Score: {ml_info.get('anomaly_score')}")
                
                if alerts:
                    for al in alerts:
                        print(f"      [!] ⚠️ ALERTA DISPARADA: [{al['type']}] {al['description']}")
                else:
                    print(f"      -> [OK] Telemetría dentro de parámetros seguros.")
            else:
                print(f"      [!] Error del servidor: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"      [!] Excepción de red: {e}")
            
        print("-" * 80)
        time.sleep(2)
        
    print("\n[OK] Simulación de trayectoria finalizada.")

if __name__ == "__main__":
    run_simulation()
