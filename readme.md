# Replay TCP Packet (Python)

Ce projet permet de rejouer des trames TCP enregistrées (ex. via Wireshark `.pcap` ou `.pcapng`) localement entre deux applications, sur un port spécifié.

---

## 🔧 Prérequis

- Python **3.11 ou supérieur**
- `git` installé
- Connexion Internet (pour installer les dépendances)

---

## 🚀 Installation

1. **Cloner ce dépôt** :

   ```bash
   git clone https://github.com/ton-utilisateur/replay_tcp_packet.git
   cd replay_tcp_packet
   ```

2. **Créer un environnement virtuel** :

Sous Windows :

```bash
python -m venv venv
venv\Scripts\activate
```

Sous Linux :

```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Installer les dépendances** :

   ```bash
   pip install -r requirements.txt
   ```

## ▶️Lancer le script

Assurez-vous que l’application cible est en écoute sur le port configuré dans le script.

```bash
python replay_tcp.py --pcap <chemin/fichier.pcap>
```

## 💥Problème

Le script fonctionne correctement pour le rejeu des trames enregistrées via WireShark mais seulement dans le sens DAQbox vers Polyview.
Ceci est dû au fait que seul côté Polyview le Port d'écoute est figé sur **11000** alors que côté DAQbox, le port d'écoute est **aléatoire** (voir l'appel de l'ouverture de la socket via la fonction **ConnectToTCPServerEx (..., TCP_ANY_LOCAL_PORT)** dans client.c )

## 🛜Répartition des ports TCP/UDP (officielle)

| Plage de ports    | Description                                                                    | À éviter ?                              |
| ----------------- | ------------------------------------------------------------------------------ | --------------------------------------- |
| **0 – 1023**      | Ports **réservés** aux services système (HTTP=80, SSH=22, etc.)                | ❌ **Oui**                              |
| **1024 – 49151**  | Ports **enregistrés** (mais pas forcément réservés). Exemple : 3306 pour MySQL | ⚠️ **Potentiellement** utilisés         |
| **49152 – 65535** | Ports **dynamiques / privés / éphémères**                                      | ✅ **Recommandé pour usage local/test** |

## 📎 Annexe : Capturer les trames sur localhost:11000 avec Wireshark

Voici comment enregistrer les paquets TCP échangés en local entre deux applications sur le port 11000 :

### 🐾 Étapes détaillées

1. Lancer Wireshark
   - Ouvre l'application Wireshark sur ton poste.
2. Sélectionner l'interface de capture adaptée
   - Sur Windows, les échanges en 127.0.0.1 ne passent pas par les cartes réseau classiques.
   - Sélectionne "Loopback Adapter" pour les échanges en 127.0.0.1 (souvent fourni par Npcap).
   - Si aucune interface loopback n'apparait, installe Npcap (https://nmap.org/npcap/).
3. Filtrer uniquement le port souhaité

   - Dans la barre de filtre Wireshark, ajoute "tcp.port == 11000" pour les échanges sur le port 11000.
   - Si tu veux échanger sur tous les ports, ajoute "tcp.port == \*" pour les échanges sur tous les ports.
   - Si tu veux filtrer uniquement les trames avec de la donnée, ajoute "tcp.len > 0" pour les échanges avec de la donnée.

     ```bash
     (tcp.port ==11000)&&ip.dst==127.0.0.1&&ip.src==127.0.0.1 and tcp.len > 0
     ```

4. Démarrer la capture
   - Clique sur le bouton "Start capturing packets".
5. Lancer les deux applications qui échangent via 127.0.0.1:11000
6. Arrêter la capture
7. Sauvegarder l'enregistrement en format `.pcap` ou `.pcapng`
