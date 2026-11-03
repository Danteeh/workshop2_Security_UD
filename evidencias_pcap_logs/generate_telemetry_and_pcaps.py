#!/usr/bin/env python3
"""
Script de Generación de Telemetría Sintética y Archivos PCAP Didácticos
Taller No. 2 - Mecanismos de Seguridad para Redes IEEE 802.3 con Servidores TCP/IP
Universidad Distrital Francisco José de Caldas
"""

import hashlib
import os
import random
import time
from scapy.all import (
    Ether, IP, TCP, UDP, ICMP, DNS, DNSQR, DNSRR, Raw, wrpcap
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def generate_caso1_syn_flood():
    packets = []
    t = time.time()
    mac_src = "00:0c:29:4f:8e:1a"
    mac_dst = "00:0c:29:7b:12:4c"
    server_ip = "192.168.50.20"
    
    # 1. Tráfico benigno previo (Handshake completo y petición HTTP)
    client_ip = "192.168.50.10"
    sport = 49152
    dport = 80
    
    # SYN
    p_syn = Ether(src=mac_src, dst=mac_dst)/IP(src=client_ip, dst=server_ip)/TCP(sport=sport, dport=dport, flags="S", seq=1000)
    p_syn.time = t
    packets.append(p_syn)
    
    # SYN-ACK
    p_synack = Ether(src=mac_dst, dst=mac_src)/IP(src=server_ip, dst=client_ip)/TCP(sport=dport, dport=sport, flags="SA", seq=5000, ack=1001)
    p_synack.time = t + 0.002
    packets.append(p_synack)
    
    # ACK
    p_ack = Ether(src=mac_src, dst=mac_dst)/IP(src=client_ip, dst=server_ip)/TCP(sport=sport, dport=dport, flags="A", seq=1001, ack=5001)
    p_ack.time = t + 0.004
    packets.append(p_ack)
    
    # HTTP GET
    http_req = "GET /index.html HTTP/1.1\r\nHost: 192.168.50.20\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
    p_http = Ether(src=mac_src, dst=mac_dst)/IP(src=client_ip, dst=server_ip)/TCP(sport=sport, dport=dport, flags="PA", seq=1001, ack=5001)/Raw(load=http_req)
    p_http.time = t + 0.010
    packets.append(p_http)
    
    # 2. Ráfaga de SYN Flood anómala (muchas fuentes, sin ACK de cierre)
    t_flood = t + 0.1
    for i in range(150):
        src_ip = f"192.168.50.{random.randint(100, 240)}"
        src_p = random.randint(1024, 65530)
        p = Ether(src=mac_src, dst=mac_dst)/IP(src=src_ip, dst=server_ip)/TCP(sport=src_p, dport=80, flags="S", seq=random.randint(10000, 90000))
        p.time = t_flood + (i * 0.001)
        packets.append(p)
        
        # El servidor responde SYN-ACK esperando el ACK (half-open)
        if i % 2 == 0:
            resp = Ether(src=mac_dst, dst=mac_src)/IP(src=server_ip, dst=src_ip)/TCP(sport=80, dport=src_p, flags="SA", seq=random.randint(50000, 99999), ack=p[TCP].seq + 1)
            resp.time = p.time + 0.0015
            packets.append(resp)
            
    out_path = os.path.join(BASE_DIR, "caso1_syn_flood.pcap")
    wrpcap(out_path, packets)
    return out_path

def generate_caso2_dns_tunneling():
    packets = []
    t = time.time()
    dns_server = "192.168.50.53"
    client_ip = "192.168.50.10"
    
    # 1. Consultas legítimas
    legit_domains = ["www.google.com", "ubuntu.archive.org", "repos.udistrital.edu.co"]
    for dom in legit_domains:
        req = Ether()/IP(src=client_ip, dst=dns_server)/UDP(sport=53000+random.randint(1,900), dport=53)/DNS(rd=1, qd=DNSQR(qname=dom, qtype="A"))
        req.time = t
        packets.append(req)
        resp = Ether()/IP(src=dns_server, dst=client_ip)/UDP(sport=53, dport=req[UDP].sport)/DNS(id=req[DNS].id, qr=1, aa=1, qd=DNSQR(qname=dom), an=DNSRR(rrname=dom, rdata="192.168.50.20"))
        resp.time = t + 0.005
        packets.append(resp)
        t += 0.05
        
    # 2. Consultas anómalas de DNS Tunneling (alta entropía, cadenas largas Base32/Base64, TXT)
    exfil_payloads = [
        "4a66396b6c7338396164666a6b6c617364666a61736466.stage1.c2-exfil.lab",
        "7738396675696173646866696173756866617364666a6b.stage2.c2-exfil.lab",
        "dGhpcy1pcy1hLXNlY3JldC1leGZpbHRyYXRpb24tcGFja2V0.auth.c2-exfil.lab",
        "8f9a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d.keys.c2-exfil.lab",
        "aW5maWx0cmF0aW9uLXNlc3Npb24tdG9rZW4tOTk0ODIzMTI.ping.c2-exfil.lab"
    ]
    for p_str in exfil_payloads:
        req = Ether()/IP(src=client_ip, dst=dns_server)/UDP(sport=54120+random.randint(1,500), dport=53)/DNS(rd=1, qd=DNSQR(qname=p_str, qtype="TXT"))
        req.time = t
        packets.append(req)
        # TXT response with encoded command
        resp = Ether()/IP(src=dns_server, dst=client_ip)/UDP(sport=53, dport=req[UDP].sport)/DNS(id=req[DNS].id, qr=1, aa=1, qd=DNSQR(qname=p_str, qtype="TXT"), an=DNSRR(rrname=p_str, type="TXT", rdata="cmd_exec_ack_OK_200"))
        resp.time = t + 0.008
        packets.append(resp)
        t += 0.02
        
    out_path = os.path.join(BASE_DIR, "caso2_dns_tunneling.pcap")
    wrpcap(out_path, packets)
    return out_path

def generate_caso5_tcp_resets():
    packets = []
    t = time.time()
    client = "192.168.50.10"
    server = "192.168.50.20"
    sport = 55100
    dport = 443
    
    # Handshake normal
    packets.append(Ether()/IP(src=client, dst=server, ttl=64)/TCP(sport=sport, dport=dport, flags="S", seq=100))
    packets[-1].time = t
    packets.append(Ether()/IP(src=server, dst=client, ttl=64)/TCP(sport=dport, dport=sport, flags="SA", seq=500, ack=101))
    packets[-1].time = t + 0.002
    packets.append(Ether()/IP(src=client, dst=server, ttl=64)/TCP(sport=sport, dport=dport, flags="A", seq=101, ack=501))
    packets[-1].time = t + 0.004
    
    # Intercambio de datos TLS Client Hello
    packets.append(Ether()/IP(src=client, dst=server, ttl=64)/TCP(sport=sport, dport=dport, flags="PA", seq=101, ack=501)/Raw(b"\x16\x03\x01\x00\x85\x01\x00...TLS ClientHello"))
    packets[-1].time = t + 0.010
    
    # Inyección súbita de paquete RST spoofed desde el medio con TTL anómalo (ttl=47) o ventana inconsistente
    p_rst = Ether()/IP(src=server, dst=client, ttl=47)/TCP(sport=dport, dport=sport, flags="R", seq=501, window=0)
    p_rst.time = t + 0.012
    packets.append(p_rst)
    
    # Segundo RST
    p_rst2 = Ether()/IP(src=client, dst=server, ttl=52)/TCP(sport=sport, dport=dport, flags="RA", seq=101, ack=501)
    p_rst2.time = t + 0.013
    packets.append(p_rst2)
    
    out_path = os.path.join(BASE_DIR, "caso5_tcp_resets.pcap")
    wrpcap(out_path, packets)
    return out_path

def generate_caso6_udp_amplification():
    packets = []
    t = time.time()
    victim = "192.168.50.20"
    reflector = "192.168.50.53"
    
    # Petición DNS ANY (tipo 255) pequeña spoofed con IP de la víctima como origen
    for i in range(10):
        req = Ether()/IP(src=victim, dst=reflector)/UDP(sport=random.randint(40000, 50000), dport=53)/DNS(rd=1, qd=DNSQR(qname="victim-domain.lab", qtype=255))
        req.time = t + (i * 0.01)
        packets.append(req)
        
        # Respuesta del reflector hacia la víctima: gigante (amplificación ~45x)
        large_payload = "X" * 1200
        resp = Ether()/IP(src=reflector, dst=victim)/UDP(sport=53, dport=req[UDP].sport)/DNS(id=req[DNS].id, qr=1, aa=1, qd=DNSQR(qname="victim-domain.lab", qtype=255), an=DNSRR(rrname="victim-domain.lab", type="TXT", rdata=large_payload))
        resp.time = req.time + 0.003
        packets.append(resp)
        
    out_path = os.path.join(BASE_DIR, "caso6_udp_amplification.pcap")
    wrpcap(out_path, packets)
    return out_path

def generate_caso7_icmp_tunnel():
    packets = []
    t = time.time()
    src_host = "192.168.50.10"
    dst_host = "192.168.50.20"
    
    # 1. Pings estándar de diagnóstico (payload típico 32 bytes)
    for seq in range(1, 4):
        req = Ether()/IP(src=src_host, dst=dst_host)/ICMP(type=8, code=0, id=0x1234, seq=seq)/Raw(b"abcdefghijklmnopqrstuvwabcdefghi")
        req.time = t
        packets.append(req)
        reply = Ether()/IP(src=dst_host, dst=src_host)/ICMP(type=0, code=0, id=0x1234, seq=seq)/Raw(b"abcdefghijklmnopqrstuvwabcdefghi")
        reply.time = t + 0.001
        packets.append(reply)
        t += 0.2
        
    # 2. Túnel ICMP anómalo (Payload gigante de 512 y 1024 bytes con texto exfiltrado / shell)
    tunnel_data = b"CMD:ls -la /etc/shadow;TOKEN=" + (b"A" * 480)
    for seq in range(100, 105):
        req = Ether()/IP(src=src_host, dst=dst_host)/ICMP(type=8, code=0, id=0x9999, seq=seq)/Raw(tunnel_data)
        req.time = t
        packets.append(req)
        reply = Ether()/IP(src=dst_host, dst=src_host)/ICMP(type=0, code=0, id=0x9999, seq=seq)/Raw(tunnel_data)
        reply.time = t + 0.002
        packets.append(reply)
        t += 0.05
        
    out_path = os.path.join(BASE_DIR, "caso7_icmp_tunnel.pcap")
    wrpcap(out_path, packets)
    return out_path

def generate_caso8_port_scan():
    packets = []
    t = time.time()
    attacker = "192.168.50.10"
    target = "192.168.50.20"
    
    target_ports = [21, 22, 23, 25, 53, 80, 110, 139, 443, 445, 3306, 5222, 5269, 8080]
    open_ports = [21, 80, 5222]
    
    for port in target_ports:
        sport = random.randint(40000, 60000)
        # SYN Scan
        req = Ether()/IP(src=attacker, dst=target)/TCP(sport=sport, dport=port, flags="S", seq=random.randint(1000, 5000))
        req.time = t
        packets.append(req)
        
        if port in open_ports:
            # SYN-ACK
            resp = Ether()/IP(src=target, dst=attacker)/TCP(sport=port, dport=sport, flags="SA", seq=random.randint(1000, 5000), ack=req[TCP].seq + 1)
            resp.time = t + 0.001
            packets.append(resp)
            # Nmap sends RST to quickly abort without full handshake
            rst = Ether()/IP(src=attacker, dst=target)/TCP(sport=sport, dport=port, flags="R", seq=req[TCP].seq + 1)
            rst.time = t + 0.002
            packets.append(rst)
        else:
            # Closed port: target returns RST-ACK
            resp = Ether()/IP(src=target, dst=attacker)/TCP(sport=port, dport=sport, flags="RA", seq=0, ack=req[TCP].seq + 1)
            resp.time = t + 0.001
            packets.append(resp)
            
        t += 0.015
        
    out_path = os.path.join(BASE_DIR, "caso8_port_scan.pcap")
    wrpcap(out_path, packets)
    return out_path

def main():
    print("=== Generando PCAPs sintéticos para el Taller 2 ===")
    pcap_files = [
        generate_caso1_syn_flood(),
        generate_caso2_dns_tunneling(),
        generate_caso5_tcp_resets(),
        generate_caso6_udp_amplification(),
        generate_caso7_icmp_tunnel(),
        generate_caso8_port_scan()
    ]
    
    hash_file = os.path.join(BASE_DIR, "hashes_sha256.txt")
    with open(hash_file, "w", encoding="utf-8") as f_hash:
        f_hash.write("================================================================================\n")
        f_hash.write("REGISTRO DE INTEGRIDAD CRIPTOGRÁFICA (SHA-256) - EVIDENCIAS DE RED\n")
        f_hash.write("Taller No. 2: Mecanismos de Seguridad para Redes IEEE 802.3 con Servidores TCP/IP\n")
        f_hash.write("Universidad Distrital Francisco José de Caldas - 2026\n")
        f_hash.write("================================================================================\n\n")
        
        for p in pcap_files:
            fname = os.path.basename(p)
            size_b = os.path.getsize(p)
            sha = get_sha256(p)
            line = f"{sha}  {fname}  ({size_b} bytes)"
            print(f"[+] Generado: {fname:28s} | Tamaño: {size_b:5d} B | SHA-256: {sha[:16]}...")
            f_hash.write(f"Archivo: {fname}\n")
            f_hash.write(f"Tamaño:  {size_b} bytes\n")
            f_hash.write(f"SHA-256: {sha}\n")
            f_hash.write("-" * 80 + "\n")
            
    print(f"\n[OK] Hashes guardados exitosamente en: {hash_file}")

if __name__ == "__main__":
    main()
