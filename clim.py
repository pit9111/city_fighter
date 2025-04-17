import http.client
import json

# Connexion à Meteostat via RapidAPI
conn = http.client.HTTPSConnection("meteostat.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "d86ec0ac76msh7329992dd8cf6c5p189bcfjsn4291599cfb32",
    'x-rapidapi-host': "meteostat.p.rapidapi.com"
}

# --- 1. Chercher les stations proches ---
latitude = 49.847
longitude = 3.278

nearby_endpoint = f"/stations/nearby?lat={latitude}&lon={longitude}"
conn.request("GET", nearby_endpoint, headers=headers)
res = conn.getresponse()
nearby_data = res.read()

stations_info = json.loads(nearby_data.decode("utf-8"))
stations_list = stations_info["data"]

# --- 2. Essayer chaque station jusqu'à trouver des données normales ---
found = False
for station in stations_list:
    station_id = station["id"]
    station_name = station["name"]["en"]

    print(f"🔎 Test de la station {station_name} (ID: {station_id})...")

    normals_endpoint = f"/stations/normals?station={station_id}&start=1981&end=2010"
    conn.request("GET", normals_endpoint, headers=headers)
    res = conn.getresponse()
    climate_data = res.read()

    try:
        climate_info = json.loads(climate_data.decode("utf-8"))
        if "data" in climate_info and climate_info["data"]:
            data = climate_info["data"]
            print(f"✅ Données trouvées pour {station_name} (ID: {station_id}) !\n")
            found = True
            break
        else:
            print(f"❌ Pas de données pour {station_name}.")
    except json.JSONDecodeError:
        print(f"❌ Erreur de décodage pour {station_name}.")

if not found:
    print("❌ Aucune station avec normales disponibles pour cette période.")
    exit()

# --- 3. Traitement des données ---
def safe_avg(months):
    valid = [x for x in months if x is not None]
    return round(sum(valid) / len(valid), 2) if valid else None

# Températures par saison
hiver = [data[11]["tavg"], data[0]["tavg"], data[1]["tavg"]]    # Déc, Janv, Fév
printemps = [data[2]["tavg"], data[3]["tavg"], data[4]["tavg"]] # Mars, Avril, Mai
ete = [data[5]["tavg"], data[6]["tavg"], data[7]["tavg"]]       # Juin, Juillet, Août
automne = [data[8]["tavg"], data[9]["tavg"], data[10]["tavg"]]  # Sept, Oct, Nov

moy_hiver = safe_avg(hiver)
moy_printemps = safe_avg(printemps)
moy_ete = safe_avg(ete)
moy_automne = safe_avg(automne)

# Précipitations
prcp_mensuelles = [m["prcp"] for m in data if m["prcp"] is not None]
moy_prcp = round(sum(prcp_mensuelles) / len(prcp_mensuelles), 2) if prcp_mensuelles else None

# Ensoleillement
tsun_mensuel = [m["tsun"] for m in data if m["tsun"] is not None]
moy_tsun = round(sum(tsun_mensuel) / len(tsun_mensuel), 2) if tsun_mensuel else None

# --- 4. Affichage des résultats ---
print("\n🌡️ Température moyenne par saison (°C) :")
print(f"Hiver : {moy_hiver} °C")
print(f"Printemps : {moy_printemps} °C")
print(f"Été : {moy_ete} °C")
print(f"Automne : {moy_automne} °C")

print("\n🌧️ Précipitations :")
if moy_prcp is not None:
    print(f"Moyenne mensuelle : {moy_prcp} mm")
else:
    print("Pas de données de précipitations disponibles.")

print("\n🌤️ Ensoleillement :")
if moy_tsun is not None:
    print(f"Moyenne mensuelle : {moy_tsun} minutes (≈ {round(moy_tsun/60, 1)} h/jour)")
else:
    print("Pas de données d'ensoleillement disponibles.")
