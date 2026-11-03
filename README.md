# GUÍA-TALLER No. 2: MECANISMOS DE SEGURIDAD PARA REDES IEEE 802.3 CON SERVIDORES TCP/IP Y SISTEMA INTELIGENTE DE RASTREO ÉTICO

**Universidad Distrital Francisco José de Caldas**  
**Facultad de Ingeniería - Proyecto Curricular de Ingeniería de Sistemas**  
**Docente:** Ing. Octavio José Salcedo Parra  
**Materia:** Mecanismos de Seguridad Informática / Fundamentos de Redes de Comunicaciones  
**Entrega:** Noviembre 14 / 2026  

---

## 📁 Estructura del Proyecto

```text
taller2_mecanismos_seguridad/
├── informe_taller2_mecanismos_seguridad.pdf    <-- Documento final compilado (30 páginas con gráficas y capturas)
├── README.md                                   <-- Guía de ejecución, inventario y sustentación
├── informe_latex/
│   ├── main.tex                                <-- Código fuente en LaTeX estructurado profesionalmente
│   ├── main.pdf                                <-- PDF generado por el compilador
│   └── images/                                 <-- 26 Figuras, capturas de consola y diagramas en alta resolución (300 DPI)
│       ├── topologia_laboratorio.png
│       ├── caso1_synflood_rates.png
│       ├── caso1_netstat_terminal.png
│       ├── caso2_dnstunnel_entropy.png
│       ├── caso2_wireshark_dns.png
│       ├── caso3_nmap_services.png
│       ├── caso3_risk_matrix.png
│       ├── caso4_ml_isolation_forest.png
│       ├── caso4_confusion_matrix.png
│       ├── caso5_tcp_resets_timeline.png
│       ├── caso5_wireshark_rst.png
│       ├── caso6_udp_amplification.png
│       ├── caso6_bandwidth_spike.png
│       ├── caso7_icmp_payload_length.png
│       ├── caso7_wireshark_icmp.png
│       ├── caso8_portscan_fanout.png
│       ├── caso8_suricata_alert.png
│       ├── caso9_siem_correlation_pipeline.png
│       ├── caso9_ai_triage_dashboard.png
│       ├── caso10_xmpp_tls_handshake.png
│       ├── caso10_tls_cert_validation.png
│       ├── parte2_arquitectura_rastreo.png
│       ├── parte2_mapa_dashboard.png
│       ├── parte2_telegram_bot.png
│       ├── parte2_swagger_api.png
│       └── parte2_geofencing_alert.png
├── evidencias_pcap_logs/
│   ├── caso1_syn_flood.pcap                    <-- Capturas sintéticas reales generadas con Scapy
│   ├── caso2_dns_tunneling.pcap
│   ├── caso5_tcp_resets.pcap
│   ├── caso6_udp_amplification.pcap
│   ├── caso7_icmp_tunnel.pcap
│   ├── caso8_port_scan.pcap
│   ├── hashes_sha256.txt                       <-- Registro formal de cadena de custodia criptográfica
│   └── generate_telemetry_and_pcaps.py         <-- Script generador de tráfico y tramas de red
├── scripts_analisis/
│   └── generate_all_figures.py                 <-- Generador automatizado de las 26 evidencias visuales
└── app_rastreo_geolocalizacion/                <-- Sistema completo de software (Parte II)
    ├── backend/
    │   ├── main.py                             <-- API REST en FastAPI (Endpoints de ingesta, registro, alertas)
    │   ├── database.py                         <-- Base de datos SQLite (dispositivos, ubicaciones, geocercas, alertas)
    │   ├── geofence.py                         <-- Motor Haversine y cálculo de distancias ortodrómicas
    │   ├── ml_anomaly.py                       <-- Detector cinemático anti-spoofing con Machine Learning
    │   └── requirements.txt                    <-- Dependencias de Python
    ├── frontend/
    │   ├── index.html                          <-- Dashboard web interactivo con Leaflet.js
    │   ├── styles.css                          <-- Estilos modernos en tema ciberseguridad / dark mode
    │   └── app.js                             <-- Lógica de mapas, capas circulares de geocerca y polling
    ├── bot_telegram/
    │   ├── telegram_tracker_bot.py             <-- Bot interactivo de Telegram con teclado nativo y simulación
    │   └── README_BOT.md                       <-- Guía de configuración con BotFather
    └── simulador_dispositivo/
        └── simulate_mobile_client.py           <-- Emulador de dispositivo móvil enviando GPS por Bogotá
```

---

## 🛡️ Resumen de la Parte I: Los 10 Casos Críticos de Red

Cada uno de los 10 casos incluye en el informe LaTeX:
1. **Situación y Contexto:** Delimitación en entorno IEEE 802.3 aislado (VLAN 50).
2. **Procedimiento de Observación:** Comandos ejecutados (PowerShell, Wireshark/TShark, Nmap, OpenSSL, Suricata).
3. **Indicadores y Análisis Técnico:** Diferenciación ontológica entre *Síntoma*, *Indicador*, *Hipótesis* y *Evidencia Confirmada*.
4. **Evidencias Visuales:** Gráficas temporales, espectros de entropía, diagramas de secuencia y capturas de terminal.
5. **Mitigación y Controles:** Medidas preventivas, detectivas, correctivas y de recuperación.
6. **Respuestas a las Preguntas de Análisis:** Rigor conceptual en gestión de recursos de kernel, protocolos de red y límites de detección.
7. **Ficha de Registro de Hallazgo:** Formato mínimo requerido con marca de tiempo, IPs, puertos, severidad, acción y hash SHA-256 verificado.

### Tabla de Integridad Criptográfica (SHA-256)
| Archivo de Evidencia PCAP | Tamaño | Hash SHA-256 |
| :--- | :---: | :--- |
| `caso1_syn_flood.pcap` | 16,128 B | `8d0e5fda4547e9cad8608aaff3412664d8a4d8e90fbb102fa4542ca2e3a070ea` |
| `caso2_dns_tunneling.pcap` | 2,594 B | `bdddff6608a856ed593186747f5e36ed5f69f2d2457b1ad8ee88f13a112ec6f0` |
| `caso5_tcp_resets.pcap` | 469 B | `083f4940a9a73111fe20f58628fa7febdf971f6ec8a0a88b6f9240e858eef082` |
| `caso6_udp_amplification.pcap` | 14,224 B | `205127ca90fff94b2ee7f3833a4595c68581fe2abb0232c3fbcf70af222db1bd` |
| `caso7_icmp_tunnel.pcap` | 6,234 B | `e0512a71b74db26dabcf514d786c31ff825973535435cc0985bf43c78cf2ae98` |
| `caso8_port_scan.pcap` | 2,194 B | `4e8907bad8c3012326e6c8a9746d5f65f788225b6a1989d6ea404c8d7ac31545` |

---

## 🛰️ Resumen de la Parte II: Sistema de Rastreo, Geofencing e Inteligencia Artificial

### 1. Viabilidad Técnica según Canal de Comunicación
* **WhatsApp:** **No es viable técnicamente** rastrear a un usuario de manera encubierta o con solo conocer su número debido al cifrado de extremo a extremo (protocolo Signal). Requiere que el usuario comparta su ubicación voluntariamente desde el chat.
* **Telegram:** Requiere un bot autorizado donde el usuario inicie la interacción (`/start`) y presione un botón de teclado personalizado (`request_location: true`). No permite rastreo silencioso en segundo plano sin consentimiento.
* **GPS Directo (App Móvil / Agente):** Método de máxima precisión satelital (2 a 5 m). Requiere permisos del sistema operativo otorgados por el usuario y transmisión periódica hacia la API REST.

### 2. Características del Sistema Implementado
* **Backend REST (FastAPI):** Endpoints documentados en Swagger (`/docs`) para registro, ingesta de telemetría y consultas.
* **Geofencing con Haversine:** Verificación ortodrómica sobre el elipsoide terrestre para detectar salidas de perímetro seguro (Campus UD Calle 40).
* **IA Cinemática Anti-Spoofing:** Detección de saltos instantáneos imposibles ($> 5\text{ km}$ en $< 15\text{ s}$) o velocidades urbanas sobrehumanas ($> 140\text{ km/h}$) para neutralizar emuladores de GPS falso (*Fake GPS*).
* **Frontend Web (Leaflet.js):** Mapa interactivo en tiempo real con marcadores, trazado de rutas históricas (polyline) y cartas de alertas.
* **Marco Legal Colombiano:** Implementado bajo la **Ley 1581 de 2012** (Habeas Data) y la **Ley 1273 de 2009** (Delitos Informáticos), garantizando consentimiento explícito, finalidad legítima y protección de datos.

---

## 🚀 Instrucciones de Ejecución

### 1. Iniciar el Servidor Backend y Dashboard Web
Desde la raíz del proyecto o desde la carpeta `app_rastreo_geolocalizacion/backend`:
```bash
python -m uvicorn main:app --app-dir "taller2_mecanismos_seguridad/app_rastreo_geolocalizacion/backend" --host 127.0.0.1 --port 8000 --reload
```
* **Dashboard Interactivo:** Abra en su navegador `http://127.0.0.1:8000/`
* **Documentación Interactiva Swagger:** `http://127.0.0.1:8000/docs`

### 2. Ejecutar el Simulador de Dispositivo Móvil
En otra ventana de terminal:
```bash
python "taller2_mecanismos_seguridad/app_rastreo_geolocalizacion/simulador_dispositivo/simulate_mobile_client.py"
```
Transmitirá una ruta realista por Bogotá (desde Campus UD Calle 40 hacia el Parque Nacional), generando salidas de geocerca y disparando la detección de anomalías cinemáticas por salto cuántico.

### 3. Ejecutar el Bot de Telegram
* **Modo Simulación Académica (sin conexión a servidores externos):**
  ```bash
  python "taller2_mecanismos_seguridad/app_rastreo_geolocalizacion/bot_telegram/telegram_tracker_bot.py"
  ```
* **Modo en Vivo (con token de @BotFather):**
  ```bash
  export TELEGRAM_BOT_TOKEN="su_token_aqui"
  python "taller2_mecanismos_seguridad/app_rastreo_geolocalizacion/bot_telegram/telegram_tracker_bot.py" --live
  ```

### 4. Compilar el Informe LaTeX
El informe ya se encuentra compilado en `informe_taller2_mecanismos_seguridad.pdf`. Si desea recompilar tras modificar `main.tex`:
```bash
cd taller2_mecanismos_seguridad/informe_latex
../../tectonic_bin/tectonic.exe main.tex
```
O utilizando cualquier distribución estándar de TeX (`pdflatex main.tex` o importando en Overleaf).
