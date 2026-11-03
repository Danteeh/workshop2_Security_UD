# GUIA-TALLER No. 2: MECANISMOS DE SEGURIDAD PARA REDES IEEE 802.3 CON SERVIDORES TCP/IP Y SISTEMA INTELIGENTE DE RASTREO ETICO

**Universidad Distrital Francisco Jose de Caldas**  
**Facultad de Ingenieria - Proyecto Curricular de Ingenieria de Sistemas**  
**Docente:** Ing. Octavio Jose Salcedo Parra  
**Materia:** Mecanismos de Seguridad Informatica / Fundamentos de Redes de Comunicaciones  
**Entrega:** Noviembre 14 / 2026  

---

## 1. Estructura del Proyecto

```text
taller2_mecanismos_seguridad/
├── informe_taller2_mecanismos_seguridad.pdf    <-- Documento final compilado (30 paginas con graficas y capturas)
├── README.md                                   <-- Guia de ejecucion, inventario y sustentacion
├── informe_latex/
│   ├── main.tex                                <-- Codigo fuente en LaTeX estructurado profesionalmente
│   ├── main.pdf                                <-- PDF generado por el compilador
│   └── images/                                 <-- 26 Figuras, capturas de consola y diagramas en alta resolucion (300 DPI)
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
│   ├── caso1_syn_flood.pcap                    <-- Capturas sinteticas reales generadas con Scapy
│   ├── caso2_dns_tunneling.pcap
│   ├── caso5_tcp_resets.pcap
│   ├── caso6_udp_amplification.pcap
│   ├── caso7_icmp_tunnel.pcap
│   ├── caso8_port_scan.pcap
│   ├── hashes_sha256.txt                       <-- Registro formal de cadena de custodia criptografica
│   └── generate_telemetry_and_pcaps.py         <-- Script generador de trafico y tramas de red
├── scripts_analisis/
│   └── generate_all_figures.py                 <-- Generador automatizado de las 26 evidencias visuales
└── app_rastreo_geolocalizacion/                <-- Sistema completo de software (Parte II)
    ├── backend/
    │   ├── main.py                             <-- API REST en FastAPI (Endpoints de ingesta, registro, alertas)
    │   ├── database.py                         <-- Base de datos SQLite (dispositivos, ubicaciones, geocercas, alertas)
    │   ├── geofence.py                         <-- Motor Haversine y calculo de distancias ortodromicas
    │   ├── ml_anomaly.py                       <-- Detector cinematico anti-spoofing con Machine Learning
    │   └── requirements.txt                    <-- Dependencias de Python
    ├── frontend/
    │   ├── index.html                          <-- Dashboard web interactivo con Leaflet.js
    │   ├── styles.css                          <-- Estilos modernos en tema ciberseguridad / dark mode
    │   └── app.js                             <-- Logica de mapas, capas circulares de geocerca y polling
    ├── bot_telegram/
    │   ├── telegram_tracker_bot.py             <-- Bot interactivo de Telegram con teclado nativo y simulacion
    │   └── README_BOT.md                       <-- Guia de configuracion con BotFather
    └── simulador_dispositivo/
        └── simulate_mobile_client.py           <-- Emulador de dispositivo movil enviando GPS por Bogota
```

---

## 2. Resumen de la Parte I: Los 10 Casos Criticos de Red

Cada uno de los 10 casos incluye en el informe LaTeX:
1. **Situacion y Contexto:** Delimitacion en entorno IEEE 802.3 aislado (VLAN 50).
2. **Procedimiento de Observacion:** Comandos ejecutados (PowerShell, Wireshark/TShark, Nmap, OpenSSL, Suricata).
3. **Indicadores y Analisis Tecnico:** Diferenciacion ontologica entre *Sintoma*, *Indicador*, *Hipotesis* y *Evidencia Confirmada*.
4. **Evidencias Visuales:** Graficas temporales, espectros de entropia, diagramas de secuencia y capturas de terminal.
5. **Mitigacion y Controles:** Medidas preventivas, detectivas, correctivas y de recuperacion.
6. **Respuestas a las Preguntas de Analisis:** Rigor conceptual en gestion de recursos de kernel, protocolos de red y limites de deteccion.
7. **Ficha de Registro de Hallazgo:** Formato minimo requerido con marca de tiempo, IPs, puertos, severidad, accion y hash SHA-256 verificado.

### Tabla de Integridad Criptografica (SHA-256)
| Archivo de Evidencia PCAP | Tamaño | Hash SHA-256 |
| :--- | :---: | :--- |
| `caso1_syn_flood.pcap` | 16,128 B | `8d0e5fda4547e9cad8608aaff3412664d8a4d8e90fbb102fa4542ca2e3a070ea` |
| `caso2_dns_tunneling.pcap` | 2,594 B | `bdddff6608a856ed593186747f5e36ed5f69f2d2457b1ad8ee88f13a112ec6f0` |
| `caso5_tcp_resets.pcap` | 469 B | `083f4940a9a73111fe20f58628fa7febdf971f6ec8a0a88b6f9240e858eef082` |
| `caso6_udp_amplification.pcap` | 14,224 B | `205127ca90fff94b2ee7f3833a4595c68581fe2abb0232c3fbcf70af222db1bd` |
| `caso7_icmp_tunnel.pcap` | 6,234 B | `e0512a71b74db26dabcf514d786c31ff825973535435cc0985bf43c78cf2ae98` |
| `caso8_port_scan.pcap` | 2,194 B | `4e8907bad8c3012326e6c8a9746d5f65f788225b6a1989d6ea404c8d7ac31545` |

---

## 3. Resumen de la Parte II: Sistema de Rastreo, Geofencing e Inteligencia Artificial

### 3.1. Viabilidad Tecnica segun Canal de Comunicacion
* **WhatsApp:** **No es viable tecnicamente** rastrear a un usuario de manera encubierta o con solo conocer su numero debido al cifrado de extremo a extremo (protocolo Signal). Requiere que el usuario comparta su ubicacion voluntariamente desde el chat.
* **Telegram:** Requiere un bot autorizado donde el usuario inicie la interaccion (`/start`) y presione un boton de teclado personalizado (`request_location: true`). No permite rastreo silencioso en segundo plano sin consentimiento.
* **GPS Directo (App Movil / Agente):** Metodo de maxima precision satelital (2 a 5 m). Requiere permisos del sistema operativo otorgados por el usuario y transmision periodica hacia la API REST.

### 3.2. Caracteristicas del Sistema Implementado
* **Backend REST (FastAPI):** Endpoints documentados en Swagger (`/docs`) para registro, ingesta de telemetria y consultas.
* **Geofencing con Haversine:** Verificacion ortodromica sobre el elipsoide terrestre para detectar salidas de perimetro seguro (Campus UD Calle 40).
* **IA Cinematica Anti-Spoofing:** Deteccion de saltos instantaneos imposibles ($> 5\text{ km}$ en $< 15\text{ s}$) o velocidades urbanas sobrehumanas ($> 140\text{ km/h}$) para neutralizar emuladores de GPS falso (*Fake GPS*).
* **Frontend Web (Leaflet.js):** Mapa interactivo en tiempo real con marcadores, trazado de rutas historicas (polyline) y cartas de alertas.
* **Marco Legal Colombiano:** Implementado bajo la **Ley 1581 de 2012** (Habeas Data) y la **Ley 1273 de 2009** (Delitos Informaticos), garantizando consentimiento explicito, finalidad legitima y proteccion de datos.

---

## 4. Instrucciones de Ejecucion

### 4.1. Iniciar el Servidor Backend y Dashboard Web
Desde la raiz del proyecto o desde la carpeta `app_rastreo_geolocalizacion/backend`:
```bash
python -m uvicorn main:app --app-dir "taller2_mecanismos_seguridad/app_rastreo_geolocalizacion/backend" --host 127.0.0.1 --port 8000 --reload
```
* **Dashboard Interactivo:** Abra en su navegador `http://127.0.0.1:8000/`
* **Documentacion Interactiva Swagger:** `http://127.0.0.1:8000/docs`

### 4.2. Ejecutar el Simulador de Dispositivo Movil
En otra ventana de terminal:
```bash
python "taller2_mecanismos_seguridad/app_rastreo_geolocalizacion/simulador_dispositivo/simulate_mobile_client.py"
```
Transmitira una ruta realista por Bogota (desde Campus UD Calle 40 hacia el Parque Nacional), generando salidas de geocerca y disparando la deteccion de anomalias cinematicas por salto cuantico.

### 4.3. Ejecutar el Bot de Telegram
* **Modo Simulacion Academica (sin conexion a servidores externos):**
  ```bash
  python "taller2_mecanismos_seguridad/app_rastreo_geolocalizacion/bot_telegram/telegram_tracker_bot.py"
  ```
* **Modo en Vivo (con token de @BotFather):**
  ```bash
  export TELEGRAM_BOT_TOKEN="su_token_aqui"
  python "taller2_mecanismos_seguridad/app_rastreo_geolocalizacion/bot_telegram/telegram_tracker_bot.py" --live
  ```

### 4.4. Compilar el Informe LaTeX
El informe ya se encuentra compilado en `informe_taller2_mecanismos_seguridad.pdf`. Si desea recompilar tras modificar `main.tex`:
```bash
cd taller2_mecanismos_seguridad/informe_latex
../../tectonic_bin/tectonic.exe main.tex
```
O utilizando cualquier distribucion estandar de TeX (`pdflatex main.tex` o importando en Overleaf).
