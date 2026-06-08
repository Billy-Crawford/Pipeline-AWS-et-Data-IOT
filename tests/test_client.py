import requests
import json
import time

API_URL = "https://4ffao75bnf.execute-api.eu-west-3.amazonaws.com/Prod/ingest"

def send_payload(payload_type, data):
    print(f"\n--- Envoi du Payload [{payload_type}] ---")
    try:
        response = requests.post(API_URL, json=data, headers={"Content-Type": "application/json"})
        print(f"Code Statut HTTP : {response.status_code}")
        print("Réponse du serveur :")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur lors de la requête : {e}")

def verifier_dynamodb_via_lambda():
    print("\n--- Récupération des données stockées dans DynamoDB (Via GET Bypass) ---")
    try:
        # On envoie un GET sur la même URL
        response = requests.get(API_URL)
        print(f"Code Statut HTTP : {response.status_code}")
        print("Contenu de la table DynamoDB :")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Erreur lors de la lecture : {e}")

# Cas de test
payload_valide = [{"device_id": "capteur-iot-lome-01", "timestamp": int(time.time()), "sensor_data": {"temperature": 26.5, "humidity": 78.2, "status": "OK"}}]
payload_anomalie = [{"device_id": "capteur-iot-lome-02", "timestamp": int(time.time()), "sensor_data": {"temperature": 42.1, "humidity": 45.0, "status": "CRITICAL"}}]
payload_corrompu = [{"device_id": "capteur-iot-lome-03", "timestamp": int(time.time()), "sensor_data": {"humidity": 60.1, "status": "OK"}}]

if __name__ == "__main__":
    # 1. On renvoie les données pour peupler la table propre
    send_payload("NOMINAL (VALIDE)", payload_valide)
    time.sleep(1)
    send_payload("ANOMALIE (STATUS CRITICAL)", payload_anomalie)
    time.sleep(1)
    send_payload("CORROMPU (METRIQUE MANQUANTE)", payload_corrompu)
    time.sleep(1)
    
    # 2. L'étape magique : On appelle le scan Cloud via notre route GET
    verifier_dynamodb_via_lambda()