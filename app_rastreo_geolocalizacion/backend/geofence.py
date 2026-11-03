"""
Motor de Geofencing y Utilidades Geoespaciales
Mecanismos de Seguridad Informática - Universidad Distrital FJDC
"""

import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcula la distancia ortodrómica en metros entre dos puntos geográficos (WGS84)
    usando la fórmula de Haversine.
    """
    R = 6371000.0  # Radio medio de la Tierra en metros
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    
    return R * c

def check_geofence(lat, lon, geofences):
    """
    Evalúa si las coordenadas dadas se encuentran dentro de las geocercas activas.
    Retorna estado ('INSIDE' o 'OUTSIDE') y detalles de la geocerca más cercana.
    """
    if not geofences:
        return {"status": "NO_GEOFENCE_DEFINED", "geofence_name": None, "distance_m": 0}

    results = []
    for g in geofences:
        dist = haversine_distance(lat, lon, g["center_lat"], g["center_lon"])
        is_inside = dist <= g["radius_meters"]
        results.append({
            "geofence_id": g["id"],
            "name": g["name"],
            "radius_m": g["radius_meters"],
            "distance_m": round(dist, 2),
            "is_inside": is_inside
        })

    # Si está dentro de al menos una geocerca activa, es seguro
    inside_fences = [r for r in results if r["is_inside"]]
    if inside_fences:
        return {
            "status": "INSIDE",
            "active_geofence": inside_fences[0]["name"],
            "distance_m": inside_fences[0]["distance_m"]
        }
    else:
        # Está fuera de todas
        closest = min(results, key=lambda x: x["distance_m"])
        return {
            "status": "OUTSIDE",
            "closest_geofence": closest["name"],
            "distance_m": closest["distance_m"],
            "delta_outside_m": round(closest["distance_m"] - closest["radius_m"], 2)
        }

def get_approximate_address(lat, lon):
    """
    Geocodificación inversa simplificada y determinística para entorno académico/laboratorio.
    """
    # Zonas de referencia en Bogotá
    if 4.625 <= lat <= 4.632 and -74.070 <= lon <= -74.062:
        return "Campus UD Calle 40, Teusaquillo / Chapinero, Bogotá D.C."
    elif 4.632 < lat <= 4.640 and -74.065 <= lon <= -74.055:
        return "Sector Parque Nacional - Javeriana, Cra 7, Bogotá D.C."
    elif 4.615 <= lat < 4.625 and -74.075 <= lon <= -74.065:
        return "Sede Macarena / Av. Circunvalar, Santafé, Bogotá D.C."
    else:
        return f"Coordenadas GPS: {lat:.6f}°N, {lon:.6f}°W (Área Metropolitana Bogotá)"
