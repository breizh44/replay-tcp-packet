import argparse
import sys
from scapy.all import rdpcap, TCP, IP
import socket
import time


# === Paramètres CLI ===
parser = argparse.ArgumentParser(description="Rejouer un fichier pcapng TCP vers localhost.")
parser.add_argument("--pcap", required=True, help="Chemin du fichier .pcap ou .pcapng")
#parser.add_argument("--timing", action="store_true", help="Respecter les délais d'origine entre les paquets")
args = parser.parse_args()

# === CONFIGURATION ===
#PCAP_FILE = "export_filtered.pcapng"
PCAP_FILE = args.pcap
DEST_IP = "127.0.0.1"
DEST_PORT = 11000
USE_TIMING = True  # True = respecte les délais entre les paquets (optionnel)
#USE_TIMING = args.timing

# === Charger les paquets ===
try:
    packets = rdpcap(PCAP_FILE)
except FileNotFoundError:
    print(f"Erreur : fichier introuvable '{PCAP_FILE}'")
    sys.exit(1)

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

if not tcp_payloads:
    print("Aucun paquet valide à envoyer trouvé.")
    sys.exit(0)

# === Établir la connexion TCP ===
try:
    # Créer un socket TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((DEST_IP, DEST_PORT))
except ConnectionRefusedError:
    print(f"Erreur : impossible de se connecter à {DEST_IP}:{DEST_PORT}")
    sys.exit(1)

print(f"Connecté à {DEST_IP}:{DEST_PORT} – envoi de {len(tcp_payloads)} messages...")

# === Rejouer les messages ===
for i, (payload, delay) in enumerate(tcp_payloads):
    if delay > 0:
        time.sleep(float(delay))
    print(f"[{i+1}] Envoi ({len(payload)} octets) : {payload}")
    s.send(payload)

s.close()
print("Terminé.")
