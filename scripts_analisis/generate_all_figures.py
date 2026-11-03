#!/usr/bin/env python3
"""
Generador de Figuras y Evidencias Visuales de Alta Resolución
Taller No. 2 - Mecanismos de Seguridad para Redes IEEE 802.3 con Servidores TCP/IP
Universidad Distrital Francisco José de Caldas
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_DIR = os.path.join(BASE_DIR, "informe_latex", "images")
os.makedirs(IMG_DIR, exist_ok=True)

# Configuración global de Matplotlib
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def save_fig(fig, filename):
    filepath = os.path.join(IMG_DIR, filename)
    fig.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"[+] Gráfica guardada: {filename}")

# ==============================================================================
# 0. Topología del Laboratorio
# ==============================================================================
def gen_topologia():
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#f8f9fa")
    ax.set_facecolor("#ffffff")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Switch Central
    sw_box = patches.FancyBboxPatch((4.0, 2.3), 2.0, 1.2, boxstyle="round,pad=0.2", facecolor="#1f77b4", edgecolor="#0d47a1", linewidth=2)
    ax.add_patch(sw_box)
    ax.text(5.0, 2.9, "Switch IEEE 802.3\nVLAN 50 Laboratorio\n(Aislado de Producción)", color="white", weight="bold", ha="center", va="center", fontsize=10)
    
    # Dispositivos
    nodes = [
        ("Equipo Analista\n192.168.50.10/24\nWireshark / SIEM", 1.5, 4.5, "#2ca02c"),
        ("Servidor Web / HTTP\n192.168.50.20/24\nNginx / Apache", 8.5, 4.5, "#d62728"),
        ("Servidor DNS Lab\n192.168.50.53/24\nBIND9 / Unbound", 1.5, 1.2, "#9467bd"),
        ("Servidor XMPP\n192.168.50.30/24\nOpenfire / ejabberd", 8.5, 1.2, "#ff7f0e"),
        ("Gateway Lab\n192.168.50.1/24\nSin Reenvío WAN", 5.0, 5.2, "#7f7f7f"),
    ]
    
    for label, x, y, col in nodes:
        box = patches.FancyBboxPatch((x-1.2, y-0.5), 2.4, 1.0, boxstyle="round,pad=0.15", facecolor=col, edgecolor="#333333", alpha=0.9)
        ax.add_patch(box)
        ax.text(x, y, label, color="white", weight="bold", ha="center", va="center", fontsize=8.5)
        # Línea al switch
        ax.annotate("", xy=(5.0, 2.9), xytext=(x, y), arrowprops=dict(arrowstyle="-", color="#555555", lw=2, ls="--"))
        
    ax.set_title("Topología de Red de Laboratorio Aislado (IEEE 802.3 - VLAN 50)", fontsize=13, weight="bold", pad=15, color="#1a237e")
    save_fig(fig, "topologia_laboratorio.png")

# ==============================================================================
# Caso 1. TCP SYN Flood
# ==============================================================================
def gen_caso1():
    t = np.linspace(0, 60, 300)
    # Tasa SYN
    syn_normal = 15 + 4 * np.sin(t / 5)
    syn_attack = np.where((t >= 15) & (t <= 45), 850 + 80 * np.random.randn(300), syn_normal)
    # Tasa SYN-ACK
    synack = np.where((t >= 15) & (t <= 30), 400 + 40 * np.random.randn(300), syn_normal * 0.95)
    synack = np.where((t > 30) & (t <= 45), 800 + 50 * np.random.randn(300), synack) # syncookies
    # Tasa ACK legítimo
    ack = np.where((t >= 15) & (t <= 30), 2, syn_normal * 0.9) # Bloqueo temporal legítimo antes de mitigar
    ack = np.where((t > 30) & (t <= 45), 14, ack) # Restauración con cookies
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(t, syn_attack, label="Paquetes TCP SYN (Peticiones)", color="#d32f2f", lw=2)
    ax.plot(t, synack, label="Paquetes TCP SYN/ACK (Respuestas servidor)", color="#1976d2", lw=1.8, ls="--")
    ax.plot(t, ack, label="Paquetes TCP ACK (Handshake completado)", color="#388e3c", lw=2)
    
    ax.axvspan(15, 30, color="#ffebee", alpha=0.6, label="Fase Ataque: Agotamiento Backlog")
    ax.axvspan(30, 45, color="#e8f5e9", alpha=0.6, label="Mitigación: TCP SYN Cookies Activo")
    ax.axvline(30, color="#2e7d32", ls=":", lw=2)
    ax.text(31, 700, "Activación de\nSYN Cookies & Rate Limiting", color="#1b5e20", fontsize=8.5, weight="bold")
    
    ax.set_xlabel("Tiempo transcurrido (segundos)", fontsize=10)
    ax.set_ylabel("Paquetes por segundo (pps)", fontsize=10)
    ax.set_title("Caso 1: Dinámica de Handshake en Ataque TCP SYN Flood y Mitigación", fontsize=11, weight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", fontsize=8.5)
    save_fig(fig, "caso1_synflood_rates.png")

def gen_terminal_image(text_lines, title, filename, width=900, height=450):
    img = Image.new("RGB", (width, height), color="#1e1e1e")
    draw = ImageDraw.Draw(img)
    # Barra de título de terminal
    draw.rectangle([0, 0, width, 28], fill="#333333")
    draw.ellipse([8, 8, 18, 18], fill="#ff5f56")
    draw.ellipse([24, 8, 34, 18], fill="#ffbd2e")
    draw.ellipse([40, 8, 50, 18], fill="#27c93f")
    draw.text((width//2 - 100, 6), title, fill="#cccccc")
    
    y = 40
    for line in text_lines:
        color = "#00ff66" if line.startswith("PS") or line.startswith("$") or line.startswith("#") else (
            "#ff5555" if "SYN_RECEIVED" in line or "ALERT" in line or "VULNERABLE" in line or "CRITICAL" in line else (
                "#ffaa00" if "WARNING" in line or "ESTABLISHED" in line else "#e0e0e0"
            )
        )
        draw.text((18, y), line, fill=color)
        y += 18
        if y > height - 20:
            break
            
    filepath = os.path.join(IMG_DIR, filename)
    img.save(filepath, dpi=(300, 300))
    print(f"[+] Terminal guardada: {filename}")

# ==============================================================================
# Caso 2. DNS Tunneling
# ==============================================================================
def gen_caso2():
    np.random.seed(42)
    # Dominios benignos: longitud corta (10-25 caracteres), entropía moderada (2.2 - 3.4)
    n_benign = 120
    len_benign = np.random.normal(16, 4, n_benign)
    ent_benign = np.random.normal(2.8, 0.35, n_benign)
    
    # Dominios de túnel DNS (exfiltración C2): longitud muy alta (40-85), entropía alta (4.1 - 4.9 Base64/Hex)
    n_mal = 45
    len_mal = np.random.normal(62, 8, n_mal)
    ent_mal = np.random.normal(4.45, 0.25, n_mal)
    
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.scatter(len_benign, ent_benign, color="#1976d2", alpha=0.7, edgecolors="none", s=50, label="Consultas DNS Legítimas (A, AAAA)")
    ax.scatter(len_mal, ent_mal, color="#d32f2f", alpha=0.85, edgecolors="#b71c1c", s=70, marker="^", label="Túnel DNS Exfiltración (TXT / C2 Encoded)")
    
    # Líneas de umbral
    ax.axvline(38, color="#ff9800", linestyle="--", lw=1.5, label="Umbral Longitud Subdominio (>38 chars)")
    ax.axhline(3.8, color="#9c27b0", linestyle="--", lw=1.5, label="Umbral Entropía Shannon (>3.8 bits)")
    
    ax.fill_between([38, 90], 3.8, 5.2, color="#ffebee", alpha=0.5, label="Zona de Alta Sospecha (IoC)")
    
    ax.set_xlim(5, 90)
    ax.set_ylim(1.5, 5.2)
    ax.set_xlabel("Longitud del Subdominio (número de caracteres)", fontsize=10)
    ax.set_ylabel("Entropía de Shannon (bits/carácter)", fontsize=10)
    ax.set_title("Caso 2: Detección de DNS Tunneling mediante Longitud y Entropía de Shannon", fontsize=11, weight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower right", fontsize=8)
    save_fig(fig, "caso2_dnstunnel_entropy.png")

# ==============================================================================
# Caso 3. Matriz de Riesgo / Criticidad
# ==============================================================================
def gen_caso3():
    fig, ax = plt.subplots(figsize=(8, 5))
    matrix = np.array([
        [1, 2, 3, 4, 5],
        [2, 4, 6, 8, 10],
        [3, 6, 9, 12, 15],
        [4, 8, 12, 16, 20],
        [5, 10, 15, 20, 25]
    ])
    
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("risk", ["#4caf50", "#8bc34a", "#ffeb3b", "#ff9800", "#f44336"])
    im = ax.imshow(matrix, cmap=cmap, origin="lower", extent=[0.5, 5.5, 0.5, 5.5])
    
    # Servicios identificados
    services = [
        ("FTP Texto Claro (21)\nCredenciales en Tránsito", 4.2, 4.3, "white"),
        ("Telnet Expuesto (23)\nSin Cifrado / Brute Force", 4.8, 4.6, "white"),
        ("HTTP Lab (80)\nSin HSTS / Sin TLS", 3.2, 3.4, "black"),
        ("XMPP sin TLS estricto (5222)\nSTARTTLS Opcional", 3.5, 2.7, "black"),
        ("SSH Hardened (22)\nClave Pública / Fail2ban", 1.8, 1.4, "black"),
    ]
    
    for name, imp, prob, txtcol in services:
        ax.plot(imp, prob, 'o', color="#111111", markersize=9)
        ax.text(imp, prob+0.25, name, ha="center", va="bottom", fontsize=7.5, weight="bold", color=txtcol,
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", alpha=0.85, edgecolor="#444444"))
                
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_xticklabels(["1: Muy Bajo", "2: Bajo", "3: Medio", "4: Alto", "5: Crítico"], fontsize=8.5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(["1: Muy Baja", "2: Baja", "3: Media", "4: Alta", "5: Crítica"], fontsize=8.5)
    ax.set_xlabel("Impacto Operativo / Confidencialidad", fontsize=10, weight="bold")
    ax.set_ylabel("Probabilidad de Explotación", fontsize=10, weight="bold")
    ax.set_title("Caso 3: Matriz de Riesgo y Criticidad de Servicios Expuestos", fontsize=11, weight="bold")
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.04)
    cbar.set_label("Nivel de Severidad de Riesgo", fontsize=8.5)
    save_fig(fig, "caso3_risk_matrix.png")

# ==============================================================================
# Caso 4. Detección de Anomalías con IA / ML
# ==============================================================================
def gen_caso4():
    from sklearn.ensemble import IsolationForest
    from sklearn.metrics import confusion_matrix
    
    np.random.seed(101)
    # Tráfico normal: conexiones moderadas, duración variable, bytes simétricos
    n_normal = 300
    conn_norm = np.random.exponential(12, n_normal) + 5
    bytes_norm = np.random.normal(450, 120, n_normal)
    
    # Tráfico anómalo: picos de conexiones/min, bytes muy altos o nulos (escaneo / flood / túnel)
    n_anom = 40
    conn_anom = np.concatenate([np.random.normal(85, 15, 20), np.random.normal(120, 20, 20)])
    bytes_anom = np.concatenate([np.random.normal(2400, 300, 20), np.random.normal(45, 10, 20)])
    
    X = np.vstack([
        np.column_stack([conn_norm, bytes_norm]),
        np.column_stack([conn_anom, bytes_anom])
    ])
    y_true = np.array([1]*n_normal + [-1]*n_anom) # 1: normal, -1: anómalo
    
    clf = IsolationForest(contamination=0.12, random_state=42)
    clf.fit(X[:200]) # Train solo con parte normal/dividido temporalmente
    y_pred = clf.predict(X)
    
    # Gráfica 1: Frontera de decisión y clusters
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.scatter(X[y_pred == 1, 0], X[y_pred == 1, 1], c="#1976d2", label="Clasificado Normal", alpha=0.6, s=40)
    ax.scatter(X[y_pred == -1, 0], X[y_pred == -1, 1], c="#d32f2f", label="Clasificado Anómalo (Alerta)", alpha=0.85, s=60, marker="x")
    
    ax.set_xlabel("Tasa de Conexiones por Minuto", fontsize=10)
    ax.set_ylabel("Bytes Promedio por Flujo", fontsize=10)
    ax.set_title("Caso 4: Detección No Supervisada con Isolation Forest en Tráfico TCP/IP", fontsize=11, weight="bold")
    ax.legend(loc="upper right", fontsize=8.5)
    ax.grid(True, linestyle=":", alpha=0.6)
    save_fig(fig, "caso4_ml_isolation_forest.png")
    
    # Gráfica 2: Matriz de Confusión
    cm = confusion_matrix(y_true, y_pred, labels=[1, -1])
    fig, ax = plt.subplots(figsize=(5.5, 4.5))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.set_title("Matriz de Confusión - Detector ML", fontsize=11, weight="bold")
    tick_marks = np.arange(2)
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(['Normal (1)', 'Anómalo (-1)'], fontsize=9)
    ax.set_yticklabels(['Normal (1)', 'Anómalo (-1)'], fontsize=9)
    
    thresh = cm.max() / 2.
    for i in range(2):
        for j in range(2):
            ax.text(j, i, format(cm[i, j], 'd'),
                     ha="center", va="center",
                     color="white" if cm[i, j] > thresh else "black", fontsize=12, weight="bold")
    ax.set_ylabel('Etiqueta Verdadera', fontsize=10)
    ax.set_xlabel('Etiqueta Predicha', fontsize=10)
    fig.colorbar(im, ax=ax, fraction=0.045)
    save_fig(fig, "caso4_confusion_matrix.png")

# ==============================================================================
# Caso 5. TCP Resets Inesperados
# ==============================================================================
def gen_caso5():
    t = np.linspace(0, 30, 200)
    # Sesiones activas normales
    active_sessions = 40 + 5 * np.sin(t / 2)
    # Ráfaga de resets
    resets = np.where((t >= 10) & (t <= 18), 35 + 8 * np.random.rand(200), np.random.poisson(1, 200))
    
    fig, ax1 = plt.subplots(figsize=(8.5, 4.5))
    color = '#1976d2'
    ax1.set_xlabel('Tiempo transcurrido (s)', fontsize=10)
    ax1.set_ylabel('Sesiones TCP Activas', color=color, fontsize=10)
    l1 = ax1.plot(t, active_sessions, color=color, lw=2, label="Sesiones Conectadas")
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()
    color = '#d32f2f'
    ax2.set_ylabel('Paquetes TCP RST / seg', color=color, fontsize=10)
    l2 = ax2.plot(t, resets, color=color, lw=1.8, ls="--", label="Tasa de Flags RST (tcp.flags.reset==1)")
    ax2.tick_params(axis='y', labelcolor=color)
    
    ax1.axvspan(10, 18, color="#ffebee", alpha=0.5)
    ax1.text(14, 25, "Inyección de RST\nDesincronización de Flujos\n(Spoofed TTL = 47 vs 64)", ha="center", fontsize=8.5, color="#b71c1c", weight="bold")
    
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right', fontsize=8.5)
    ax1.set_title("Caso 5: Correlación Temporal de Cierres Abruptos y Flags TCP RST", fontsize=11, weight="bold")
    ax1.grid(True, linestyle=":", alpha=0.6)
    save_fig(fig, "caso5_tcp_resets_timeline.png")

# ==============================================================================
# Caso 6. UDP Reflexión / Amplificación
# ==============================================================================
def gen_caso6():
    protocols = ['DNS (ANY)', 'NTP (monlist)', 'SSDP (M-SEARCH)', 'SNMP (GetBulk)', 'Memcached']
    req_sizes = [45, 48, 90, 60, 50]
    resp_sizes = [2400, 26700, 2700, 3600, 50000] # Factores reales
    amplification = [round(resp / req, 1) for req, resp in zip(req_sizes, resp_sizes)]
    
    x = np.arange(len(protocols))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(9, 4.8))
    rects1 = ax.bar(x - width/2, req_sizes, width, label='Tamaño Petición Spoofed (Bytes)', color='#1976d2')
    rects2 = ax.bar(x + width/2, [r/10 for r in resp_sizes], width, label='Tamaño Respuesta Reflejada / 10 (Bytes)', color='#d32f2f')
    
    ax.set_ylabel('Bytes (Escala ajustada)', fontsize=10)
    ax.set_title('Caso 6: Factor de Asimetría y Amplificación UDP por Protocolo', fontsize=11, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(protocols, fontsize=8.5)
    ax.legend(loc="upper left", fontsize=8.5)
    ax.grid(True, axis="y", linestyle=":", alpha=0.6)
    
    for i, amp in enumerate(amplification):
        ax.text(x[i] + width/2, (resp_sizes[i]/10) + 50, f"Factor:\n~{amp}x", ha='center', va='bottom', fontsize=8, weight='bold', color='#b71c1c')
        
    save_fig(fig, "caso6_udp_amplification.png")
    
    # Ancho de banda saturado
    fig2, ax_bw = plt.subplots(figsize=(8.5, 4))
    t = np.linspace(0, 40, 200)
    bw_normal = 2.5 + 0.5 * np.sin(t)
    bw_attack = np.where((t >= 10) & (t <= 30), 940 + 30 * np.random.randn(200), bw_normal)
    ax_bw.plot(t, bw_attack, color="#d32f2f", lw=2, label="Tráfico Inbound Gateway (Mbps)")
    ax_bw.axhline(1000, color="#b71c1c", ls="--", label="Límite Físico Enlace Gigabit (1 Gbps)")
    ax_bw.axvspan(10, 30, color="#ffebee", alpha=0.5, label="Reflexión Masiva No Solicitada")
    ax_bw.set_xlabel("Tiempo (s)", fontsize=10)
    ax_bw.set_ylabel("Ancho de Banda Saturado (Mbps)", fontsize=10)
    ax_bw.set_title("Caso 6: Saturación del Enlace por Tráfico Reflejado UDP", fontsize=11, weight="bold")
    ax_bw.legend(loc="center right", fontsize=8.5)
    ax_bw.grid(True, linestyle=":", alpha=0.6)
    save_fig(fig2, "caso6_bandwidth_spike.png")

# ==============================================================================
# Caso 7. ICMP: Escaneo y Payloads Atípicos
# ==============================================================================
def gen_caso7():
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    
    # Tamaños de paquete
    np.random.seed(77)
    normal_ping = np.random.choice([32, 56, 64], size=180, p=[0.7, 0.2, 0.1])
    tunnel_ping = np.concatenate([np.random.normal(512, 12, 60), np.random.normal(1024, 25, 40)])
    
    ax.hist(normal_ping, bins=np.arange(0, 1150, 32), color="#1976d2", alpha=0.7, label="ICMP Diagnóstico Estándar (32-64 B)", edgecolor="black")
    ax.hist(tunnel_ping, bins=np.arange(0, 1150, 32), color="#d32f2f", alpha=0.8, label="ICMP Tunneling / Exfiltración (512-1024 B)", edgecolor="black")
    
    ax.set_xlabel("Tamaño del Payload ICMP (Bytes)", fontsize=10)
    ax.set_ylabel("Frecuencia de Paquetes", fontsize=10)
    ax.set_title("Caso 7: Distribución de Tamaños de Payload ICMP (Normal vs Encapsulación)", fontsize=11, weight="bold")
    ax.legend(loc="upper right", fontsize=8.5)
    ax.grid(True, linestyle=":", alpha=0.6)
    save_fig(fig, "caso7_icmp_payload_length.png")

# ==============================================================================
# Caso 8. Escaneo de Puertos (Fan-out)
# ==============================================================================
def gen_caso8():
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 993, 1433, 3306, 3389, 5222, 5432, 8080]
    time_offset = np.linspace(0.1, 2.5, len(ports))
    
    status = ['Open' if p in [21, 80, 5222] else 'Closed' for p in ports]
    colors = ['#2e7d32' if s == 'Open' else '#c62828' for s in status]
    
    for i, (p, t, s, c) in enumerate(zip(ports, time_offset, status, colors)):
        ax.scatter(t, p, color=c, s=90, edgecolors="#222222", zorder=3)
        ax.annotate(f"{p} ({s})", (t + 0.04, p), fontsize=8, va="center")
        
    ax.plot(time_offset, ports, color="#757575", linestyle="--", alpha=0.5, zorder=1)
    ax.set_xlabel("Tiempo transcurrido (segundos)", fontsize=10)
    ax.set_ylabel("Puerto de Destino (TCP dport)", fontsize=10)
    ax.set_title("Caso 8: Patrón Secuencial de Escaneo SYN (Fan-Out hacia 192.168.50.20)", fontsize=11, weight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    
    # Custom legend
    open_patch = patches.Patch(color='#2e7d32', label='Puerto Abierto (SYN/ACK recibido)')
    closed_patch = patches.Patch(color='#c62828', label='Puerto Cerrado (RST/ACK recibido)')
    ax.legend(handles=[open_patch, closed_patch], loc="lower right", fontsize=8.5)
    save_fig(fig, "caso8_portscan_fanout.png")

# ==============================================================================
# Caso 9. Priorización de Alertas y SIEM
# ==============================================================================
def gen_caso9():
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor="#f8f9fa")
    ax.set_facecolor("#ffffff")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')
    
    # Cajas del Pipeline
    boxes = [
        ("Fuentes de Red\nFirewall, Zeek, Suricata,\nAuth.log, Nginx", 1.2, 2.5, "#455a64"),
        ("Normalización\ny Deduplicación\n(Logstash / Fluentd)", 3.4, 2.5, "#0288d1"),
        ("Correlación SIEM\nMulti-fuente &\nFeatures Agregadas", 5.6, 2.5, "#7b1fa2"),
        ("Modelo IA / LLM\nTriage Asistido &\nScoring Explicable", 7.8, 2.5, "#ef6c00"),
        ("Analista SOC\nValidación Humana\n(Human-in-the-Loop)", 9.3, 2.5, "#2e7d32"),
    ]
    
    for label, x, y, col in boxes:
        width = 1.3 if x < 9 else 1.1
        box = patches.FancyBboxPatch((x-width/2, y-0.9), width, 1.8, boxstyle="round,pad=0.1", facecolor=col, edgecolor="#222222")
        ax.add_patch(box)
        ax.text(x, y, label, color="white", weight="bold", ha="center", va="center", fontsize=7.5)
        if x < 9:
            ax.annotate("", xy=(x + width/2 + 0.4, y), xytext=(x + width/2, y),
                        arrowprops=dict(arrowstyle="->", color="#333333", lw=2))
                        
    ax.set_title("Caso 9: Pipeline de Ingestión, Normalización, Correlación SIEM y Triage con IA", fontsize=11, weight="bold", pad=15)
    save_fig(fig, "caso9_siem_correlation_pipeline.png")

# ==============================================================================
# Caso 10. Mensajería XMPP y TLS Handshake
# ==============================================================================
def gen_caso10():
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Líneas de vida
    ax.axvline(2.5, color="#1976d2", lw=2)
    ax.axvline(7.5, color="#d32f2f", lw=2)
    ax.text(2.5, 7.6, "Cliente XMPP\n(Gajim / Pidgin)", ha="center", weight="bold", color="#1976d2", fontsize=9.5)
    ax.text(7.5, 7.6, "Servidor XMPP\n(Openfire / ejabberd)", ha="center", weight="bold", color="#d32f2f", fontsize=9.5)
    
    steps = [
        (6.8, "1. TCP Handshake (Puerto 5222)", "->", "#666666"),
        (6.1, "2. <stream:stream> Negociación XMPP", "->", "#0288d1"),
        (5.4, "3. <features><starttls xmlns='...'/></features>", "<-", "#0288d1"),
        (4.7, "4. <starttls/> Solicitud de Upgrade", "->", "#0288d1"),
        (4.0, "5. <proceed/> Servidor Acepta TLS", "<-", "#0288d1"),
        (3.3, "6. TLS Client Hello (Cipher Suites)", "->", "#7b1fa2"),
        (2.6, "7. TLS Server Hello + Certificate + Key Exchange", "<-", "#7b1fa2"),
        (1.9, "8. Client Key Exchange + Finished", "->", "#7b1fa2"),
        (1.2, "9. Datos XMPP Cifrados en Túnel TLS (Application Data)", "<->", "#2e7d32"),
    ]
    
    for y, label, direction, col in steps:
        if direction == "->":
            ax.annotate("", xy=(7.5, y), xytext=(2.5, y), arrowprops=dict(arrowstyle="->", color=col, lw=1.8))
            ax.text(5.0, y + 0.15, label, ha="center", fontsize=8, color=col, weight="bold")
        elif direction == "<-":
            ax.annotate("", xy=(2.5, y), xytext=(7.5, y), arrowprops=dict(arrowstyle="->", color=col, lw=1.8))
            ax.text(5.0, y + 0.15, label, ha="center", fontsize=8, color=col, weight="bold")
        else:
            ax.annotate("", xy=(7.5, y), xytext=(2.5, y), arrowprops=dict(arrowstyle="<->", color=col, lw=2.5, ls="--"))
            ax.text(5.0, y + 0.15, label, ha="center", fontsize=8, color=col, weight="bold")
            
    ax.set_title("Caso 10: Flujo de Negociación STARTTLS y Cifrado de Canal en XMPP", fontsize=11, weight="bold", pad=10)
    save_fig(fig, "caso10_xmpp_tls_handshake.png")

# ==============================================================================
# Parte II. Figuras de Arquitectura, Mapas y Bot
# ==============================================================================
def gen_parte2_figs():
    # 1. Arquitectura de Parte II
    fig, ax = plt.subplots(figsize=(9.5, 5.5), facecolor="#f8f9fa")
    ax.set_facecolor("#ffffff")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')
    
    components = [
        ("Cliente Móvil\n(GPS / HTML5 Geoloc)", 1.5, 5.2, "#1976d2"),
        ("Bot de Telegram\n(@GeoTrackerSafeBot)", 1.5, 2.0, "#0088cc"),
        ("API Gateway / FastAPI\nBackend Servidor REST\n(Token Auth & TLS)", 5.5, 3.6, "#2e7d32"),
        ("Base de Datos SQLite\n(Historial, Nodos, Hashes)", 9.0, 5.2, "#5e35b1"),
        ("Motor Geofencing &\nDetector Anomalías ML", 9.0, 2.0, "#d81b60"),
        ("Dashboard Web\n(Leaflet.js / OpenStreetMap)", 5.5, 6.2, "#f57c00"),
    ]
    
    for label, x, y, col in components:
        w = 2.4
        h = 1.1
        box = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.15", facecolor=col, edgecolor="#222222")
        ax.add_patch(box)
        ax.text(x, y, label, color="white", weight="bold", ha="center", va="center", fontsize=8)
        
    # Conexiones
    arrows = [
        ((1.5, 4.6), (4.3, 3.8), "POST /api/location\n(JSON + GPS Coords)"),
        ((1.5, 2.6), (4.3, 3.4), "Webhook / REST\n(User Shared Coord)"),
        ((6.7, 4.1), (7.8, 5.0), "ORM / SQL Write"),
        ((6.7, 3.2), (7.8, 2.3), "Feature Stream"),
        ((5.5, 4.2), (5.5, 5.6), "WebSocket / Polling (Live Feed)"),
    ]
    for start, end, lbl in arrows:
        ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color="#424242", lw=1.8))
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y, lbl, fontsize=7, ha="center", va="center", color="#333333",
                bbox=dict(boxstyle="square,pad=0.1", facecolor="#ffffff", alpha=0.8, edgecolor="none"))
                
    ax.set_title("Parte II: Arquitectura Completa del Sistema de Rastreo Ético y Detección de Anomalías", fontsize=11, weight="bold", pad=15)
    save_fig(fig, "parte2_arquitectura_rastreo.png")
    
    # 2. Mapa y Dashboard Leaflet (Render visual)
    fig, ax = plt.subplots(figsize=(8.5, 5.5), facecolor="#f0f2f5")
    ax.set_facecolor("#e8eaed")
    
    # Simulación de cuadrícula y calles de Bogotá (UD Sede Calle 40)
    ax.set_xlim(-74.075, -74.055)
    ax.set_ylim(4.620, 4.640)
    
    # Calles y avenidas
    for y_street in np.linspace(4.622, 4.638, 9):
        ax.axhline(y_street, color="#ffffff", lw=2, alpha=0.8)
    for x_street in np.linspace(-74.073, -74.057, 9):
        ax.axvline(x_street, color="#ffffff", lw=2, alpha=0.8)
        
    # Zona de Geofence (UD Sede Central - radio 450m)
    geofence_center = (-74.065, 4.628)
    circle = plt.Circle(geofence_center, 0.004, color='#4caf50', alpha=0.25, label="Geocerca Autorizada (Radio 450 m)")
    circle_border = plt.Circle(geofence_center, 0.004, color='#2e7d32', fill=False, lw=2, ls="--")
    ax.add_patch(circle)
    ax.add_patch(circle_border)
    
    # Ruta de trayectoria
    track_lons = [-74.068, -74.066, -74.065, -74.064, -74.062, -74.059]
    track_lats = [4.624, 4.626, 4.628, 4.631, 4.634, 4.637]
    ax.plot(track_lons, track_lats, color="#1976d2", lw=2.5, ls="-", marker="o", label="Historial de Puntos GPS (Últimas 2 hrs)")
    
    # Posición actual
    ax.scatter([-74.059], [4.637], color="#d32f2f", s=140, zorder=5, marker="*", label="Posición Actual Dispositivo (+57 310...)")
    
    ax.text(-74.065, 4.628, "Campus UD Calle 40\n(Zona Segura)", color="#1b5e20", weight="bold", ha="center", fontsize=8)
    ax.text(-74.059, 4.638, "ALERTA: Salida de Geocerca\n4.6370°N, 74.0590°W", color="#b71c1c", weight="bold", ha="center", fontsize=7.5,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#ffffff", edgecolor="#b71c1c"))
            
    ax.set_xlabel("Longitud (°W)", fontsize=9.5)
    ax.set_ylabel("Latitud (°N)", fontsize=9.5)
    ax.set_title("Parte II: Visualización en Mapa Interactivo Leaflet.js con Geocercado", fontsize=11, weight="bold")
    ax.legend(loc="lower right", fontsize=8)
    save_fig(fig, "parte2_mapa_dashboard.png")

# ==============================================================================
# Capturas de Consola / Terminales Realistas
# ==============================================================================
def gen_terminal_captures():
    # Terminal 1: Netstat SYN_RECEIVED
    t1_lines = [
        "PS C:\\Windows\\system32> netstat -ano -p tcp | Select-String \"192.168.50.20:80\"",
        "  Proto  Dirección local          Dirección remota        Estado          PID",
        "  TCP    192.168.50.20:80         192.168.50.142:49312    SYN_RECEIVED    4216",
        "  TCP    192.168.50.20:80         192.168.50.187:51204    SYN_RECEIVED    4216",
        "  TCP    192.168.50.20:80         192.168.50.103:39811    SYN_RECEIVED    4216",
        "  TCP    192.168.50.20:80         192.168.50.219:60124    SYN_RECEIVED    4216",
        "  TCP    192.168.50.20:80         192.168.50.111:44901    SYN_RECEIVED    4216",
        "  TCP    192.168.50.20:80         192.168.50.155:58210    SYN_RECEIVED    4216",
        "  TCP    192.168.50.20:80         192.168.50.198:33190    SYN_RECEIVED    4216",
        "  TCP    192.168.50.20:80         192.168.50.10:49152     ESTABLISHED     4216",
        "PS C:\\Windows\\system32> Get-Process -Id 4216 | Select-Object ProcessName, Path, CPU, WorkingSet64",
        "ProcessName Path                                CPU       WorkingSet64",
        "----------- ----                                ---       ------------",
        "nginx       C:\\nginx\\nginx.exe                   48.92     145620992   ",
        "PS C:\\Windows\\system32> # ALERTA: Cola de conexiones pendientes (Backlog) saturada (150+ SYN_RECEIVED)"
    ]
    gen_terminal_image(t1_lines, "Administrador: Windows PowerShell - Inspección de Conexiones TCP", "caso1_netstat_terminal.png", 900, 380)

    # Terminal 2: Wireshark DNS Tunneling
    t2_lines = [
        "tshark -r caso2_dns_tunneling.pcap -Y \"dns\" -T fields -e frame.number -e ip.src -e dns.qry.name -e dns.qry.type -e dns.txt",
        "  1   192.168.50.10   www.google.com                            1 (A)     -",
        "  2   192.168.50.53   www.google.com                            1 (A)     -",
        "  3   192.168.50.10   repos.udistrital.edu.co                   1 (A)     -",
        "  5   192.168.50.10   4a66396b6c7338396164666a6b.c2-exfil.lab   16 (TXT)  -",
        "  6   192.168.50.53   4a66396b6c7338396164666a6b.c2-exfil.lab   16 (TXT)  \"cmd_exec_ack_OK_200\"",
        "  7   192.168.50.10   dGhpcy1pcy1hLXNlY3JldC1leG.c2-exfil.lab   16 (TXT)  -",
        "  8   192.168.50.53   dGhpcy1pcy1hLXNlY3JldC1leG.c2-exfil.lab   16 (TXT)  \"session_key_received\"",
        "  9   192.168.50.10   8f9a2b3c4d5e6f7a8b9c0d1e2f.c2-exfil.lab   16 (TXT)  -",
        "# INDICADOR CONFIRMADO: Subdominios Base64/Hex exfiltrando datos por canal encubierto UDP/53"
    ]
    gen_terminal_image(t2_lines, "TShark - Inspección de Paquetes DNS y Carga Útil TXT", "caso2_wireshark_dns.png", 900, 320)

    # Terminal 3: Nmap Servicios Heredados
    t3_lines = [
        "analyst@soc-workstation:~$ nmap -sV -sC -Pn -p- 192.168.50.20",
        "Starting Nmap 7.94 ( https://nmap.org ) at 2026-11-03 10:15 -05",
        "Nmap scan report for 192.168.50.20",
        "Host is up (0.00045s latency).",
        "PORT     STATE SERVICE       VERSION",
        "21/tcp   open  ftp           ProFTPD 1.3.5 (Vulnerable: mod_copy CVE-2015-3306)",
        "| ftp-anon: Anonymous FTP login permitted (Free disk space: 42.1GB)",
        "22/tcp   open  ssh           OpenSSH 8.9p1 Ubuntu 3ubuntu0.6 (Ubuntu Linux; protocol 2.0)",
        "23/tcp   open  telnet        Linux telnetd (Texto claro sin autenticación segura)",
        "80/tcp   open  http          Apache httpd 2.4.41 ((Ubuntu) mod_ssl/2.4.41 OpenSSL/1.1.1f)",
        "|_http-server-header: Apache/2.4.41 (Ubuntu)",
        "5222/tcp open  jabber        Openfire XMPP Server 4.7.1",
        "Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel",
        "WARNING: Protocolos en texto plano (FTP/Telnet/HTTP) expuestos sin filtrado de acceso."
    ]
    gen_terminal_image(t3_lines, "Bash - Escaneo de Puertos y Detección de Versiones con Nmap", "caso3_nmap_services.png", 900, 380)

    # Terminal 4: Wireshark TCP RST
    t4_lines = [
        "tshark -r caso5_tcp_resets.pcap -Y \"tcp.flags.reset==1\" -T fields -e frame.number -e ip.src -e ip.dst -e ip.ttl -e tcp.srcport -e tcp.dstport -e tcp.seq -e tcp.window_size",
        "  5   192.168.50.20   192.168.50.10   47    443   55100   501   0",
        "  6   192.168.50.10   192.168.50.20   52    55100 443     101   0",
        "# ANÁLISIS FORENSE:",
        "Frame 5: TCP RST inyectado desde dispositivo intermedio spoofing la IP del Servidor.",
        "Discrepancia de TTL detectada: TTL esperado = 64 (LAN), TTL recibido = 47.",
        "Tamaño de ventana TCP = 0. Cierre forzoso de sesión TLS sin intercambio de close_notify."
    ]
    gen_terminal_image(t4_lines, "TShark - Correlación de Resets Anómalos y Discrepancias de TTL", "caso5_wireshark_rst.png", 900, 300)

    # Terminal 5: ICMP Wireshark
    t5_lines = [
        "tshark -r caso7_icmp_tunnel.pcap -Y \"icmp.type == 8\" -T fields -e frame.number -e ip.src -e ip.dst -e data.len -e data.text",
        "  1   192.168.50.10   192.168.50.20   32    \"abcdefghijklmnopqrstuvwabcdefghi\"",
        "  3   192.168.50.10   192.168.50.20   32    \"abcdefghijklmnopqrstuvwabcdefghi\"",
        "  7   192.168.50.10   192.168.50.20   512   \"CMD:ls -la /etc/shadow;TOKEN=AAAAAA...\"",
        "  9   192.168.50.10   192.168.50.20   512   \"CMD:cat /etc/passwd;STDOUT=root:x:...\"",
        "# EVIDENCIA CONFIRMADA: Tráfico ICMP encapsula comandos y exfiltración de credenciales."
    ]
    gen_terminal_image(t5_lines, "TShark - Inspección de Carga Útil en Tramas ICMP Echo Request", "caso7_wireshark_icmp.png", 900, 270)

    # Terminal 6: Suricata Alert
    t6_lines = [
        "root@suricata-sensor:/var/log/suricata# tail -n 6 fast.log",
        "11/03/2026-10:18:22.104291 [**] [1:2001219:19] ET SCAN Potential Nmap SYN Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.50.10:49210 -> 192.168.50.20:21",
        "11/03/2026-10:18:22.120349 [**] [1:2001219:19] ET SCAN Potential Nmap SYN Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.50.10:49211 -> 192.168.50.20:23",
        "11/03/2026-10:18:22.135112 [**] [1:2001219:19] ET SCAN Potential Nmap SYN Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.50.10:49212 -> 192.168.50.20:80",
        "11/03/2026-10:18:22.150882 [**] [1:2001219:19] ET SCAN Potential Nmap SYN Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {TCP} 192.168.50.10:49213 -> 192.168.50.20:5222",
        "REGLA PROCESADA: alert tcp $EXTERNAL_NET any -> $HOME_NET any (flags:S; threshold: type both, track by_src, count 10, seconds 5; msg:\"PORT SCAN DETECTADO\"; sid:1000088; rev:1;)"
    ]
    gen_terminal_image(t6_lines, "Suricata IDS - Registro de Alertas en fast.log y Detección de Barrido", "caso8_suricata_alert.png", 950, 270)

    # Terminal 7: OpenSSL Cert Validation (Caso 10)
    t7_lines = [
        "analyst@soc-workstation:~$ openssl s_client -connect 192.168.50.30:5222 -starttls xmpp -showcerts",
        "CONNECTED(00000003)",
        "depth=0 C = CO, ST = Bogota, O = Universidad Distrital, CN = xmpp.lab.local",
        "verify error:num=18:self-signed certificate",
        "verify return:1",
        "---",
        "Certificate chain",
        " 0 s:C = CO, ST = Bogota, O = Universidad Distrital, CN = xmpp.lab.local",
        "   i:C = CO, ST = Bogota, O = Universidad Distrital, CN = xmpp.lab.local",
        "   Validity: NotBefore: Oct 20 12:00:00 2024 GMT; NotAfter : Oct 20 12:00:00 2025 GMT [EXPIRED]",
        "---",
        "New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384",
        "HALLAZGO: Certificado autofirmado y CADUCADO. Vulnerable a ataques Man-in-the-Middle si el cliente no valida CA."
    ]
    gen_terminal_image(t7_lines, "OpenSSL - Auditoría de Certificados XMPP y Negociación TLS", "caso10_tls_cert_validation.png", 900, 360)

    # Terminal 8: AI Triage Dashboard (Caso 9)
    t8_lines = [
        "[SIEM CORRELATION & AI TRIAGE ENGINE v3.4] - Incident #INC-2026-8841",
        "--------------------------------------------------------------------------------",
        "Score de Riesgo Global: 88 / 100 [CRÍTICO] | Confianza del Modelo: 94.6%",
        "Entidad Afectada: 192.168.50.20 (Servidor Web & Aplicación)",
        "Fuentes Correlacionadas: 4 (Suricata IDS, Zeek Conn Log, Nginx Access, Auth.log)",
        "",
        "RESUMEN EJECUTIVO GENERADO POR LLM (Explicable):",
        "1. Patrón convergente: Escaneo previo SYN de puertos (10:18:22) por IP 192.168.50.10.",
        "2. Identificación del servicio FTP ProFTPD 1.3.5 vulnerable a ejecución remota de código.",
        "3. Ráfaga secundaria de peticiones HTTP POST con cargas útiles de inyección.",
        "",
        "RECOMENDACIÓN DE TRIAGE:",
        "[ ] Aislamiento Preventivo de Red para host 192.168.50.10 (Requiere Aprobación Humana).",
        "[X] Aplicación de regla de filtrado dinámico en Gateway de Laboratorio.",
        "ESTADO: PENDIENTE DE REVISIÓN POR ANALISTA TIER 2."
    ]
    gen_terminal_image(t8_lines, "Wazuh / Elastic SIEM - Triage de Incidentes Asistido por Inteligencia Artificial", "caso9_ai_triage_dashboard.png", 900, 380)

    # Terminal 9: Telegram Bot Chat (Parte II)
    t9_lines = [
        "Telegram Messenger - Chat con @GeoTrackerSecurityBot",
        "================================================================================",
        "[Bot] ¡Bienvenido al Sistema de Rastreo y Seguridad Móvil (Laboratorio UD)!",
        "      Para registrar este dispositivo, ingrese su número con código de país.",
        "[Usuario] +57 3108892341",
        "[Bot] Dispositivo verificado exitosamente. Token de sesión: tk_sec_9941a",
        "      Presione el botón inferior para compartir su ubicación en tiempo real.",
        "      [ 📍 COMPARTIR MI UBICACIÓN ACTUAL ]  <-- (Botón nativo Telegram)",
        "[Usuario] *Ubicación enviada: Lat: 4.628031, Lon: -74.065120, Precisión: 4.2m*",
        "[Bot] ✅ Coordenadas registradas e indexadas en la API REST.",
        "      Geocodificación: Cra 7 # 40-53, Chapinero, Bogotá D.C.",
        "      Estado Geofence: 'DENTRO DE ZONA SEGURA (Campus UD)'",
        "      Velocidad calculada: 0.0 km/h [NORMAL - ML Score: 0.02]"
    ]
    gen_terminal_image(t9_lines, "Telegram Client - Interacción con el Bot y Transmisión de Coordenadas", "parte2_telegram_bot.png", 900, 360)

    # Terminal 10: Swagger API (Parte II)
    t10_lines = [
        "FastAPI Interactive API Documentation (Swagger UI) - http://localhost:8000/docs",
        "================================================================================",
        "POST   /api/v1/devices/register      Registrar nuevo dispositivo por teléfono",
        "POST   /api/v1/location/report       Ingestar coordenadas GPS y telemetría",
        "GET    /api/v1/devices               Listar dispositivos y estado en tiempo real",
        "GET    /api/v1/location/{device_id}  Consultar última ubicación conocida",
        "GET    /api/v1/history/{device_id}   Consultar historial de rutas por fecha",
        "GET    /api/v1/alerts                Consultar alertas de Geofencing y ML",
        "POST   /api/v1/geofence/set          Definir zonas geográficas seguras (polígonos)",
        "",
        "Response 200 OK: {",
        "  \"status\": \"success\",",
        "  \"device_id\": \"DEV-573108892341\",",
        "  \"geofence_status\": \"BREACH_DETECTED\",",
        "  \"anomaly_detected\": false,",
        "  \"distance_to_center_km\": 1.42",
        "}"
    ]
    gen_terminal_image(t10_lines, "FastAPI - Endpoints de la API REST para Rastreo y Geofencing", "parte2_swagger_api.png", 900, 380)

    # Terminal 11: Geofencing Alert (Parte II)
    t11_lines = [
        "[MOTOR DE REGLAS Y DETECCIÓN CINEMÁTICA - ALERTA DE SEGURIDAD]",
        "================================================================================",
        "ID Evento: ALR-2026-00492 | Marca de Tiempo: 2026-11-03 10:28:15 UTC-5",
        "Dispositivo: +57 3108892341 (Usuario: Estudiante Lab UD)",
        "Coordenadas actuales: Lat: 4.637012, Lon: -74.059044",
        "Última posición previa: Lat: 4.628031, Lon: -74.065120 (Hace 120 segundos)",
        "",
        "[!] TIPO DE ALERTA: SALIDA DE ZONA SEGURA (GEOFENCING BREACH)",
        "    Distancia al perímetro seguro (Campus UD): 1.14 km fuera del radio.",
        "",
        "[!] REVISIÓN DE IA / ML CINEMÁTICO:",
        "    Velocidad promedio calculada: 34.2 km/h (Desplazamiento vehicular normal).",
        "    Validación Anti-Spoofing: Consistente (No hay salto cuántico / teletransportación).",
        "    Acción tomada: Notificación Push emitida a consola administrativa."
    ]
    gen_terminal_image(t11_lines, "Motor de Alertas - Detección de Violación de Geocerca y Telemetría", "parte2_geofencing_alert.png", 900, 360)

def main():
    print("=== Generando Figuras y Evidencias Visuales para el Informe ===")
    gen_topologia()
    gen_caso1()
    gen_caso2()
    gen_caso3()
    gen_caso4()
    gen_caso5()
    gen_caso6()
    gen_caso7()
    gen_caso8()
    gen_caso9()
    gen_caso10()
    gen_parte2_figs()
    gen_terminal_captures()
    print("\n[OK] Todas las figuras han sido generadas en:", IMG_DIR)

if __name__ == "__main__":
    main()
