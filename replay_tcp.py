from scapy.all import rdpcap, TCP, IP
import socket
import time

# === CONFIGURATION ===
#PCAP_FILE = "export_filtered.pcapng"
PCAP_FILE = "simple_exploitation.pcapng"
DEST_IP = "127.0.0.1"
DEST_PORT = 11000
USE_TIMING = True  # True = respecte les délais entre les paquets (optionnel)

# === Charger les paquets ===
packets = rdpcap(PCAP_FILE)

# === Filtrer les paquets TCP utiles ===
tcp_payloads = []
last_time = None

for pkt in packets:
    if IP in pkt and TCP in pkt and pkt[TCP].payload:
        # Paquet en direction de 127.0.0.1:11000
        if pkt[IP].dst == DEST_IP and pkt[TCP].dport == DEST_PORT:
            payload = bytes(pkt[TCP].payload)
            timestamp = pkt.time
            if USE_TIMING:
                delay = 0
                if last_time is not None:
                    delay = timestamp - last_time
                last_time = timestamp
                tcp_payloads.append((payload, delay))
            else:
                tcp_payloads.append((payload, 0))

# === Établir la connexion TCP ===
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((DEST_IP, DEST_PORT))
print(f"Connecté à {DEST_IP}:{DEST_PORT} – envoi de {len(tcp_payloads)} messages...")

# === Rejouer les messages ===
for i, (payload, delay) in enumerate(tcp_payloads):
    if delay > 0:
        time.sleep(float(delay))
    print(f"[{i+1}] Envoi ({len(payload)} octets) : {payload}")
    s.send(payload)

s.close()
print("Terminé.")
