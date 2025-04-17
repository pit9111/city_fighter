import requests

# Connexion RapidAPI
headers = {
    "x-rapidapi-key": "d86ec0ac76msh7329992dd8cf6c5p189bcfjsn4291599cfb32",
    "x-rapidapi-host": "meteostat.p.rapidapi.com"
}

# Latitude / Longitude données
latitude = 49.847
longitude = 3.278

# 1. Chercher les stations proches
url_nearby = "https://meteostat.p.rapidapi.com/stations/nearby"
params_nearby = {"lat": latitude, "lon": longitude}
response_nearby = requests.get(url_nearby, headers=headers, params=params_nearby)
stations = response_nearby.json()["data"]

# 2. Essayer chaque station jusqu'à trouver des données normales
found = False
for station in stations:
    station_id = station["id"]
    station_name = station["name"]["en"]

    print(f"🔎 Test de la station {station_name} ({station_id})...")

    url_normals = "https://meteostat.p.rapidapi.com/stations/normals"
    params_normals = {"station": station_id, "start": "1961", "end": "1990"}
    response_normals = requests.get(url_normals, headers=headers, params=params_normals)

    response_json = response_normals.json()

    # Vérifier si "data" existe dans la réponse
    if "data" in response_json and response_json["data"]:
        print(f"✅ Données trouvées pour {station_name} ({station_id}) !")
        print(response_json["data"])
        found = True
        break
    else:
        print(f"❌ Pas de données pour {station_name} ({station_id}).")

if not found:
    print("❌ Aucune station avec normales disponibles pour cette période.")
