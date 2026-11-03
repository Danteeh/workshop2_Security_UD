"""
Base de Datos SQLite para Sistema de Rastreo Seguro
Mecanismos de Seguridad Informática - Universidad Distrital FJDC
"""

import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracker.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Tabla de dispositivos registrados (por número telefónico)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devices (
        device_id TEXT PRIMARY KEY,
        phone_number TEXT UNIQUE NOT NULL,
        device_name TEXT NOT NULL,
        auth_token TEXT NOT NULL,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        consent_accepted INTEGER DEFAULT 1
    );
    """)
    
    # Tabla de historial de ubicaciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        accuracy REAL DEFAULT 5.0,
        speed REAL DEFAULT 0.0,
        battery_level REAL DEFAULT 100.0,
        address TEXT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (device_id) REFERENCES devices (device_id)
    );
    """)
    
    # Tabla de configuración de geocercas (Geofencing)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS geofences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        center_lat REAL NOT NULL,
        center_lon REAL NOT NULL,
        radius_meters REAL NOT NULL,
        is_active INTEGER DEFAULT 1
    );
    """)
    
    # Tabla de alertas de seguridad y anomalías
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT NOT NULL,
        alert_type TEXT NOT NULL, -- GEOFENCE_EXIT, GEOFENCE_ENTER, ANOMALY_SPOOFING, HIGH_SPEED
        severity TEXT NOT NULL,   -- LOW, MEDIUM, HIGH, CRITICAL
        description TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_resolved INTEGER DEFAULT 0,
        FOREIGN KEY (device_id) REFERENCES devices (device_id)
    );
    """)
    
    # Insertar geocerca por defecto (Campus UD Sede Calle 40)
    cursor.execute("SELECT COUNT(*) FROM geofences")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO geofences (name, center_lat, center_lon, radius_meters, is_active)
        VALUES ('Campus UD Calle 40 - Zona Segura', 4.628031, -74.065120, 500.0, 1)
        """)
        
    # Insertar dispositivo de prueba de laboratorio
    cursor.execute("SELECT COUNT(*) FROM devices")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO devices (device_id, phone_number, device_name, auth_token, is_active, consent_accepted)
        VALUES ('DEV-573108892341', '+57 310 8892341', 'Terminal Móvil Analista 01', 'token_laboratorio_sec_2026', 1, 1)
        """)
        
    conn.commit()
    conn.close()
    print("[+] Base de datos SQLite inicializada en:", DB_PATH)

if __name__ == "__main__":
    init_db()
