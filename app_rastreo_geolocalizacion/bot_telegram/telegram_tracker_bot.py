#!/usr/bin/env python3
"""
Bot de Telegram para Captura Etica y Autorizada de Ubicacion
Taller No. 2 - Mecanismos de Seguridad Informatica
Universidad Distrital Francisco Jose de Caldas - 2026

Caracteristicas Tecnicas:
- Cumple con las restricciones de Telegram: no puede rastrear sin consentimiento explicito.
- Solicita ubicacion mediante boton nativo 'Send Location' (ReplyKeyboardMarkup).
- Envia las coordenadas geoespaciales recibidas al Backend REST (FastAPI).
- Permite modo en vivo (con Token de BotFather) y modo simulacion de laboratorio.
"""

import sys
import time
import json
import os
import requests

API_BACKEND_URL = os.getenv("TRACKER_BACKEND_URL", "http://127.0.0.1:8000/api/v1")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SIMULATION_MODE")

class TelegramTrackerBot:
    def __init__(self, token=TELEGRAM_BOT_TOKEN, backend_url=API_BACKEND_URL):
        self.token = token
        self.backend_url = backend_url
        self.api_url = f"https://api.telegram.org/bot{self.token}"
        self.registered_users = {} # chat_id -> device_id & token

    def send_message_with_keyboard(self, chat_id, text):
        """
        Envia un mensaje con el teclado personalizado nativo para solicitar ubicacion y contacto.
        """
        keyboard = {
            "keyboard": [
                [{"text": "Compartir mi Ubicacion Actual", "request_location": True}],
                [{"text": "Compartir mi Telefono (Registro)", "request_contact": True}],
                [{"text": "Informacion y Privacidad (Habeas Data)"}]
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
        
        payload = {
            "chat_id": chat_id,
            "text": text,
            "reply_markup": json.dumps(keyboard),
            "parse_mode": "Markdown"
        }
        
        try:
            r = requests.post(f"{self.api_url}/sendMessage", json=payload, timeout=5)
            return r.json()
        except Exception as e:
            print(f"[!] Error al enviar mensaje Telegram: {e}")
            return None

    def relay_location_to_backend(self, device_id, token, lat, lon):
        """
        Transmite las coordenadas GPS capturadas al backend de seguridad.
        """
        endpoint = f"{self.backend_url}/location/report"
        payload = {
            "device_id": device_id,
            "token": token,
            "latitude": lat,
            "longitude": lon,
            "accuracy": 4.5,
            "battery_level": 92.0
        }
        try:
            resp = requests.post(endpoint, json=payload, timeout=5)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"[!] Backend respondio error {resp.status_code}: {resp.text}")
                return None
        except Exception as e:
            print(f"[!] No se pudo conectar al Backend REST: {e}")
            return None

    def run_simulation(self):
        """
        Simulacion interactiva para pruebas de laboratorio cuando no se dispone
        de token activo o conectividad hacia los servidores de Telegram.
        """
        print("================================================================================")
        print("   TELEGRAM TRACKER BOT - SIMULADOR INTERACTIVO DE LABORATORIO ACADEMICO        ")
        print("   Materia: Mecanismos de Seguridad Informatica - Universidad Distrital FJDC    ")
        print("================================================================================")
        print("[*] Modo: Simulacion Local Activo.")
        print("[*] Backend destino:", self.backend_url)
        print("\n--- PASO 1: Simular Inicio de Conversacion (/start) ---")
        chat_id = 99881122
        user_phone = "+57 310 8892341"
        device_id = "DEV-573108892341"
        auth_token = "token_laboratorio_sec_2026"
        
        print(f"[BOT -> Usuario {chat_id}]:")
        welcome_msg = (
            "*Bienvenido a GeoTracker Safe Bot*\n"
            "Este servicio permite la geolocalizacion consentida para emergencias y monitoreo seguro.\n"
            "Conforme a la Ley 1581 de 2012 (Habeas Data), su ubicacion solo se capturara si presiona el boton.\n"
            "Presione *Compartir mi Ubicacion Actual*."
        )
        print(welcome_msg)
        
        print("\n--- PASO 2: Simular Disparador de Boton de Ubicacion de Usuario ---")
        sim_coords = [
            (4.628031, -74.065120, "Campus UD Calle 40 (Dentro de Geocerca Segura)"),
            (4.631500, -74.062000, "Carrera 7 con Calle 42 (Desplazamiento Peatonal)"),
            (4.637012, -74.059044, "Sector Parque Nacional (Alerta: Salida de Geocerca)")
        ]
        
        for lat, lon, desc in sim_coords:
            print(f"\n[Usuario]: Presiona boton 'Compartir Ubicacion' -> Coords: ({lat}, {lon}) [{desc}]")
            print("[*] Transmitiendo coordenadas al Backend REST...")
            res = self.relay_location_to_backend(device_id, auth_token, lat, lon)
            if res:
                geo_st = res.get("geofence_status")
                addr = res.get("address")
                alerts = res.get("alerts_triggered", [])
                print(f"[BOT -> Usuario]: [OK] Ubicacion recibida y procesada:")
                print(f"      Direccion: {addr}")
                print(f"      Estado Geocerca: {geo_st}")
                if alerts:
                    print(f"      [ALERTA GENERADA] {alerts[0]['type']} - {alerts[0]['description']}")
            else:
                print(f"[*] Simulacion completada (Backend no alcanzable en modo standalone).")
            time.sleep(1)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token or token == "SIMULATION_MODE":
            print("[!] Para modo --live debe definir la variable de entorno TELEGRAM_BOT_TOKEN.")
            sys.exit(1)
        bot = TelegramTrackerBot(token=token)
        print(f"[+] Iniciando Bot de Telegram en modo real con Token: {token[:8]}...")
        # Polling real
        offset = 0
        while True:
            try:
                r = requests.get(f"{bot.api_url}/getUpdates?offset={offset}&timeout=10", timeout=15)
                data = r.json()
                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    msg = upd.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    if "text" in msg:
                        txt = msg["text"]
                        if txt == "/start":
                            bot.send_message_with_keyboard(chat_id, "Bienvenido. Comparta su ubicacion con el boton inferior.")
                    elif "location" in msg:
                        loc = msg["location"]
                        bot.relay_location_to_backend("DEV-573108892341", "token_laboratorio_sec_2026", loc["latitude"], loc["longitude"])
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                time.sleep(2)
    else:
        bot = TelegramTrackerBot()
        bot.run_simulation()

if __name__ == "__main__":
    main()
