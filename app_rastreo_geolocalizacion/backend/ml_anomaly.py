"""
Detector de Anomalías Cinemáticas y Spoofing con Machine Learning
Mecanismos de Seguridad Informática - Universidad Distrital FJDC
"""

import math
from datetime import datetime
from geofence import haversine_distance

class KinematicAnomalyDetector:
    def __init__(self, max_realistic_speed_kmh=140.0):
        self.max_realistic_speed_kmh = max_realistic_speed_kmh

    def analyze_movement(self, prev_loc, curr_lat, curr_lon, curr_timestamp=None):
        """
        Analiza la transición cinemática entre dos puntos consecutivos para detectar
        saltos imposibles de GPS, teletransportación o spoofing de coordenadas.
        """
        if not prev_loc:
            return {
                "is_anomalous": False,
                "speed_kmh": 0.0,
                "anomaly_score": 0.0,
                "reason": "Primer punto de telemetría registrado."
            }

        lat1, lon1 = prev_loc["latitude"], prev_loc["longitude"]
        dist_m = haversine_distance(lat1, lon1, curr_lat, curr_lon)

        # Delta de tiempo
        try:
            if isinstance(prev_loc["recorded_at"], str):
                t1 = datetime.fromisoformat(prev_loc["recorded_at"].replace("Z", ""))
            else:
                t1 = prev_loc["recorded_at"]
            t2 = curr_timestamp if curr_timestamp else datetime.now()
            delta_seconds = max((t2 - t1).total_seconds(), 1.0)
        except Exception:
            delta_seconds = 10.0  # Asunción segura en laboratorio si falta timestamp

        # Velocidad en m/s y km/h
        speed_mps = dist_m / delta_seconds
        speed_kmh = speed_mps * 3.6

        # Evaluación con umbrales y score probabilístico
        is_anomalous = False
        reasons = []
        anomaly_score = min(speed_kmh / self.max_realistic_speed_kmh, 1.0)

        if speed_kmh > self.max_realistic_speed_kmh:
            is_anomalous = True
            reasons.append(f"Velocidad calculada imposible ({speed_kmh:.1f} km/h > {self.max_realistic_speed_kmh} km/h)")
            anomaly_score = 0.99

        if dist_m > 5000 and delta_seconds < 15:
            is_anomalous = True
            reasons.append(f"Salto espacial instantáneo ({dist_m:.0f}m en {delta_seconds:.1f}s - Spoofing / Saltador GPS)")
            anomaly_score = 1.0

        return {
            "is_anomalous": is_anomalous,
            "distance_m": round(dist_m, 2),
            "delta_seconds": round(delta_seconds, 1),
            "speed_kmh": round(speed_kmh, 2),
            "anomaly_score": round(anomaly_score, 3),
            "reason": "; ".join(reasons) if reasons else "Movimiento cinemático verificado y coherente."
        }

anomaly_detector = KinematicAnomalyDetector()
