"""
Backend API REST - Servidor de Rastreo, Geofencing y Detección de Anomalías
Taller No. 2 - Mecanismos de Seguridad Informática
Universidad Distrital Francisco José de Caldas
"""

import os
import uuid
import secrets
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from database import init_db, get_db
from geofence import check_geofence, get_approximate_address, haversine_distance
from ml_anomaly import anomaly_detector

app = FastAPI(
    title="API de Rastreo de Dispositivos y Geofencing Seguro",
    description="Servidor REST para recolección de telemetría GPS, geocercas y detección inteligente de anomalías cinemáticas.",
    version="2.0.0"
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Base de Datos en el arranque
@app.on_event("startup")
def on_startup():
    init_db()

# Modelos Pydantic
class DeviceRegisterRequest(BaseModel):
    phone_number: str = Field(..., example="+57 310 8892341")
    device_name: str = Field(..., example="Teléfono Laboratorio Docente")
    consent_accepted: bool = Field(True, example=True)

class LocationReportRequest(BaseModel):
    device_id: str = Field(..., example="DEV-573108892341")
    token: str = Field(..., example="token_laboratorio_sec_2026")
    latitude: float = Field(..., example=4.628031)
    longitude: float = Field(..., example=-74.065120)
    accuracy: float = Field(5.0, example=3.5)
    speed: Optional[float] = Field(0.0, example=15.2)
    battery_level: Optional[float] = Field(100.0, example=87.5)

class GeofenceCreateRequest(BaseModel):
    name: str = Field(..., example="Zona Segura - Biblioteca Central")
    center_lat: float = Field(..., example=4.628500)
    center_lon: float = Field(..., example=-74.065500)
    radius_meters: float = Field(..., example=300.0)

# ==============================================================================
# Endpoints de la API REST
# ==============================================================================

@app.post("/api/v1/devices/register", summary="Registrar nuevo dispositivo por número telefónico")
def register_device(payload: DeviceRegisterRequest):
    if not payload.consent_accepted:
        raise HTTPException(status_code=400, detail="Debe aceptar expresamente el consentimiento de rastreo (Habeas Data).")
        
    conn = get_db()
    cursor = conn.cursor()
    
    clean_phone = payload.phone_number.strip().replace(" ", "").replace("-", "")
    device_id = f"DEV-{clean_phone.replace('+', '')}"
    auth_token = f"tk_{secrets.token_hex(16)}"
    
    try:
        cursor.execute("""
        INSERT INTO devices (device_id, phone_number, device_name, auth_token, consent_accepted)
        VALUES (?, ?, ?, ?, 1)
        ON CONFLICT(phone_number) DO UPDATE SET
            device_name=excluded.device_name,
            auth_token=excluded.auth_token,
            is_active=1
        """, (device_id, payload.phone_number, payload.device_name, auth_token))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
        
    conn.close()
    return {
        "status": "success",
        "message": "Dispositivo registrado exitosamente.",
        "device_id": device_id,
        "phone_number": payload.phone_number,
        "auth_token": auth_token
    }

@app.get("/api/v1/devices", summary="Listar dispositivos registrados y su última ubicación")
def list_devices():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT d.device_id, d.phone_number, d.device_name, d.registered_at, d.is_active,
           l.latitude, l.longitude, l.accuracy, l.speed, l.battery_level, l.address, l.recorded_at
    FROM devices d
    LEFT JOIN (
        SELECT * FROM locations WHERE id IN (
            SELECT MAX(id) FROM locations GROUP BY device_id
        )
    ) l ON d.device_id = l.device_id
    ORDER BY d.registered_at DESC
    """)
    rows = cursor.fetchall()
    devices = []
    for r in rows:
        devices.append(dict(r))
    conn.close()
    return {"devices": devices}

@app.post("/api/v1/location/report", summary="Ingestar reporte de ubicación GPS con validación de seguridad")
def report_location(payload: LocationReportRequest):
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Validar autenticación de dispositivo
    cursor.execute("SELECT * FROM devices WHERE device_id = ? AND auth_token = ?", (payload.device_id, payload.token))
    device = cursor.fetchone()
    if not device:
        conn.close()
        raise HTTPException(status_code=401, detail="Credenciales inválidas o dispositivo no autorizado.")
        
    # 2. Consultar última ubicación previa para análisis cinemático
    cursor.execute("SELECT * FROM locations WHERE device_id = ? ORDER BY id DESC LIMIT 1", (payload.device_id,))
    prev_loc = cursor.fetchone()
    prev_loc_dict = dict(prev_loc) if prev_loc else None
    
    # 3. Análisis de anomalías cinemáticas (Spoofing / Saltos imposibles)
    ml_result = anomaly_detector.analyze_movement(prev_loc_dict, payload.latitude, payload.longitude)
    
    # 4. Evaluación de Geofencing
    cursor.execute("SELECT * FROM geofences WHERE is_active = 1")
    active_geofences = [dict(g) for g in cursor.fetchall()]
    geo_result = check_geofence(payload.latitude, payload.longitude, active_geofences)
    
    # 5. Geocodificación inversa
    address = get_approximate_address(payload.latitude, payload.longitude)
    
    # 6. Guardar nueva ubicación
    cursor.execute("""
    INSERT INTO locations (device_id, latitude, longitude, accuracy, speed, battery_level, address)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (payload.device_id, payload.latitude, payload.longitude, payload.accuracy, 
          ml_result["speed_kmh"], payload.battery_level, address))
          
    # 7. Disparar alertas si corresponde
    alerts_triggered = []
    if geo_result.get("status") == "OUTSIDE":
        alert_desc = f"Dispositivo ha salido de las zonas seguras autorizadas. Ubicación: {address}. Distancia fuera: {geo_result.get('delta_outside_m')}m"
        cursor.execute("""
        INSERT INTO alerts (device_id, alert_type, severity, description, latitude, longitude)
        VALUES (?, 'GEOFENCE_EXIT', 'HIGH', ?, ?, ?)
        """, (payload.device_id, alert_desc, payload.latitude, payload.longitude))
        alerts_triggered.append({"type": "GEOFENCE_EXIT", "description": alert_desc})
        
    if ml_result.get("is_anomalous"):
        alert_desc = f"Posible Spoofing GPS / Manipulación: {ml_result.get('reason')}"
        cursor.execute("""
        INSERT INTO alerts (device_id, alert_type, severity, description, latitude, longitude)
        VALUES (?, 'ANOMALY_SPOOFING', 'CRITICAL', ?, ?, ?)
        """, (payload.device_id, alert_desc, payload.latitude, payload.longitude))
        alerts_triggered.append({"type": "ANOMALY_SPOOFING", "description": alert_desc})
        
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "device_id": payload.device_id,
        "geofence_status": geo_result.get("status"),
        "geofence_details": geo_result,
        "kinematic_analysis": ml_result,
        "address": address,
        "alerts_triggered": alerts_triggered
    }

@app.get("/api/v1/history/{device_id}", summary="Consultar historial de trayectorias")
def get_history(device_id: str, limit: int = 100):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT id, latitude, longitude, accuracy, speed, battery_level, address, recorded_at
    FROM locations
    WHERE device_id = ?
    ORDER BY id ASC
    LIMIT ?
    """, (device_id, limit))
    points = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"device_id": device_id, "total_points": len(points), "trail": points}

@app.get("/api/v1/geofence", summary="Listar geocercas activas")
def get_geofences():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM geofences WHERE is_active = 1")
    fences = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"geofences": fences}

@app.post("/api/v1/geofence", summary="Crear nueva geocerca")
def create_geofence(payload: GeofenceCreateRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO geofences (name, center_lat, center_lon, radius_meters, is_active)
    VALUES (?, ?, ?, ?, 1)
    """, (payload.name, payload.center_lat, payload.center_lon, payload.radius_meters))
    conn.commit()
    fence_id = cursor.lastrowid
    conn.close()
    return {"status": "success", "id": fence_id, "name": payload.name}

@app.get("/api/v1/alerts", summary="Consultar eventos de alerta y violaciones")
def get_alerts():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, d.phone_number, d.device_name
    FROM alerts a
    JOIN devices d ON a.device_id = d.device_id
    ORDER BY a.id DESC
    LIMIT 50
    """)
    alerts = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"alerts": alerts}

# Servir archivos estáticos del frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", summary="Dashboard Interactivo de Rastreo")
def serve_dashboard():
    index_file = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "API de Rastreo Activa. Ingrese a /docs para la documentación interactiva."}
