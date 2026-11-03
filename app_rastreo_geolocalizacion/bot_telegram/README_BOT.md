# Guía de Configuración y Despliegue del Bot de Telegram

## 1. Contexto y Restricciones de Telegram
A diferencia de aplicaciones nativas de rastreo directo por GPS en el sistema operativo (Android/iOS), **la API de Telegram impone salvaguardas estrictas de privacidad**:
1. **Consentimiento Explícito:** Un bot de Telegram **no puede** solicitar ni extraer la ubicación de un usuario en segundo plano de manera autónoma o silenciosa.
2. **Interacción Iniciada por el Usuario:** El usuario debe iniciar el chat (`/start`) y presionar expresamente un botón de teclado nativo configurado con `request_location: true`.
3. **Restricción de Terceros:** Telegram no permite vincular una cuenta únicamente consultando el número telefónico desde el exterior si el usuario no ha iniciado el diálogo con el bot ni ha compartido su tarjeta de contacto (`request_contact: true`).

## 2. Pasos para Configurar en Producción (BotFather)
1. Abra Telegram y busque al usuario oficial `@BotFather`.
2. Envíe el comando `/newbot` y siga las instrucciones (asigne un nombre y un alias único terminado en `bot`, ej. `UD_GeoTracker_Sec_Bot`).
3. Copie el token generado (ej. `7182938475:AAH_xExampleToken...`).
4. Configure la variable de entorno:
   ```bash
   export TELEGRAM_BOT_TOKEN="7182938475:AAH_xExampleToken..."
   export TRACKER_BACKEND_URL="http://192.168.50.20:8000/api/v1"
   ```
5. Ejecute el bot:
   ```bash
   python telegram_tracker_bot.py --live
   ```

## 3. Modo Simulación de Laboratorio
Para pruebas académicas aisladas sin conexión a servidores externos:
```bash
python telegram_tracker_bot.py
```
El script ejecutará el flujo completo de simulación: bienvenida, emisión de teclado nativo, recepción de coordenadas simuladas y transmisión cifrada hacia la API REST.
