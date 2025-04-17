import streamlit as st
import pandas as pd
import requests

# Configuration de la page en mode "wide"
st.set_page_config(page_title="Comparateur de Communes", layout="wide")

# Chargement des données depuis le CSV avec mise en cache
@st.cache_data
def load_data():
    df = pd.read_csv("communes_synthetique.csv")
    return df

# Requête SPARQL : récupérer l'URL de l'article Wikipédia correspondant à un code INSEE
@st.cache_data
def get_wikipedia_title_from_insee(insee_code):
    query = f"""
    SELECT ?article WHERE {{
      ?ville wdt:P374 "{insee_code}".
      ?article schema:about ?ville;
               schema:inLanguage "fr";
               schema:isPartOf <https://fr.wikipedia.org/>.
    }}
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"Accept": "application/sparql-results+json"}
    response = requests.get(url, params={'query': query, 'format': 'json'}, headers=headers)
    if response.status_code != 200:
        return None
    data = response.json()
    results = data.get("results", {}).get("bindings", [])
    if results:
        full_url = results[0]["article"]["value"]
        # Extraction du titre à partir de l'URL (la partie après "/wiki/")
        title = full_url.split("/wiki/")[-1]
        return title
    return None

# Récupération de l'image via l'API REST de Wikipédia
@st.cache_data
def get_wikipedia_thumbnail(title):
    url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{title}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        image_url = data.get("thumbnail", {}).get("source", None)
        city_name = data.get("title", None)
        extract = data.get("extract", None)
        return image_url, city_name, extract
    return None, None, None

# 🌦️ Récupération de la météo prévisionnelle
@st.cache_data
def get_weather_forecast(insee_code):
    import requests

    TOKEN = "53ed6fa76d3c503a4d2577a7d14909104244f231fdf3fc9cbd639b146073801b"
    url = f"https://api.meteo-concept.com/api/forecast/daily?token={TOKEN}&insee={insee_code}"

    weather_codes = {0: "Soleil", 1: "Peu nuageux", 2: "Ciel voilé", 3: "Nuageux", 4: "Très nuageux", 5: "Couvert",6: "Brouillard", 7: "Brouillard givrant", 10: "Pluie faible", 11: "Pluie modérée", 12: "Pluie forte",13: "Pluie faible verglaçante", 14: "Pluie modérée verglaçante", 15: "Pluie forte verglaçante",16: "Bruine", 20: "Neige faible", 21: "Neige modérée", 22: "Neige forte",
    30: "Pluie et neige mêlées faibles", 31: "Pluie et neige mêlées modérées", 32: "Pluie et neige mêlées fortes",40: "Averses de pluie locales et faibles", 41: "Averses de pluie locales", 42: "Averses locales et fortes",43: "Averses de pluie faibles", 44: "Averses de pluie", 45: "Averses de pluie fortes",46: "Averses de pluie faibles et fréquentes", 47: "Averses de pluie fréquentes", 48: "Averses de pluie fortes et fréquentes",60: "Averses de neige localisées et faibles", 61: "Averses de neige localisées", 62: "Averses de neige localisées et fortes",63: "Averses de neige faibles", 64: "Averses de neige", 65: "Averses de neige fortes",66: "Averses de neige faibles et fréquentes", 67: "Averses de neige fréquentes", 68: "Averses de neige fortes et fréquentes",
    70: "Averses de pluie et neige mêlées localisées et faibles", 71: "Averses de pluie et neige mêlées localisées",72: "Averses de pluie et neige mêlées localisées et fortes", 73: "Averses de pluie et neige mêlées faibles",74: "Averses de pluie et neige mêlées", 75: "Averses de pluie et neige mêlées fortes",76: "Averses de pluie et neige mêlées faibles et nombreuses", 77: "Averses de pluie et neige mêlées fréquentes",78: "Averses de pluie et neige mêlées fortes et fréquentes",
    100: "Orages faibles et locaux", 101: "Orages locaux", 102: "Orages forts et locaux",103: "Orages faibles", 104: "Orages", 105: "Orages forts", 106: "Orages faibles et fréquents",107: "Orages fréquents", 108: "Orages forts et fréquents",120: "Orages faibles et locaux de neige ou grésil", 121: "Orages locaux de neige ou grésil",
    122: "Orages modérés de neige ou grésil", 123: "Orages faibles de neige ou grésil",124: "Orages de neige ou grésil", 125: "Orages forts de neige ou grésil",126: "Orages faibles et fréquents de neige ou grésil", 127: "Orages fréquents de neige ou grésil",128: "Orages forts et fréquents de neige ou grésil",
    130: "Orages faibles et locaux de pluie et neige mêlées ou grésil",131: "Orages locaux de pluie et neige mêlées ou grésil",132: "Orages forts et locaux de pluie et neige mêlées ou grésil",133: "Orages faibles de pluie et neige mêlées ou grésil",
    134: "Orages de pluie et neige mêlées ou grésil",135: "Orages forts de pluie et neige mêlées ou grésil",136: "Orages faibles et fréquents de pluie et neige mêlées ou grésil",137: "Orages fréquents de pluie et neige mêlées ou grésil",138: "Orages forts et fréquents de pluie et neige mêlées ou grésil",140: "Pluies orageuses", 141: "Pluie et neige mêlées à caractère orageux", 142: "Neige à caractère orageux",
    210: "Pluie faible intermittente", 211: "Pluie modérée intermittente", 212: "Pluie forte intermittente",220: "Neige faible intermittente", 221: "Neige modérée intermittente", 222: "Neige forte intermittente",230: "Pluie et neige mêlées", 231: "Pluie et neige mêlées", 232: "Pluie et neige mêlées",235: "Averses de grêle"
}

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        forecasts = []
        for item in data['forecast'][:4]:  # Prochains 4 jours
            forecasts.append({
                "date": item['datetime'][:10],
                "weather": weather_codes.get(item['weather'], f"Code {item['weather']}"),
                "tmin": item['tmin'],
                "tmax": item['tmax'],
                "wind": item['wind10m'],
                "sun_hours": item['sun_hours']
            })
        return forecasts
    else:
        return None


# Fonction pour récupérer les normales climatiques d'une commune
@st.cache_data
def get_climate_data(latitude, longitude):
    import http.client
    import json

    conn = http.client.HTTPSConnection("meteostat.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "d86ec0ac76msh7329992dd8cf6c5p189bcfjsn4291599cfb32",
        'x-rapidapi-host': "meteostat.p.rapidapi.com"
    }

    # Trouver les stations proches
    nearby_endpoint = f"/stations/nearby?lat={latitude}&lon={longitude}"
    conn.request("GET", nearby_endpoint, headers=headers)
    res = conn.getresponse()
    nearby_data = res.read()

    stations_info = json.loads(nearby_data.decode("utf-8"))
    stations_list = stations_info.get("data", [])

    for station in stations_list:
        station_id = station["id"]

        normals_endpoint = f"/stations/normals?station={station_id}&start=1981&end=2010"
        conn.request("GET", normals_endpoint, headers=headers)
        res = conn.getresponse()
        climate_data = res.read()

        try:
            climate_info = json.loads(climate_data.decode("utf-8"))
            if "data" in climate_info and climate_info["data"]:
                data = climate_info["data"]

                # Calculs
                def safe_avg(months):
                    valid = [x for x in months if x is not None]
                    return round(sum(valid) / len(valid), 2) if valid else None

                hiver = [data[11]["tavg"], data[0]["tavg"], data[1]["tavg"]]
                printemps = [data[2]["tavg"], data[3]["tavg"], data[4]["tavg"]]
                ete = [data[5]["tavg"], data[6]["tavg"], data[7]["tavg"]]
                automne = [data[8]["tavg"], data[9]["tavg"], data[10]["tavg"]]

                moy_hiver = safe_avg(hiver)
                moy_printemps = safe_avg(printemps)
                moy_ete = safe_avg(ete)
                moy_automne = safe_avg(automne)

                prcp_mensuelles = [m["prcp"] for m in data if m["prcp"] is not None]
                moy_prcp = round(sum(prcp_mensuelles) / len(prcp_mensuelles), 2) if prcp_mensuelles else None

                tsun_mensuel = [m["tsun"] for m in data if m["tsun"] is not None]
                moy_tsun = round(sum(tsun_mensuel) / len(tsun_mensuel), 2) if tsun_mensuel else None

                return {
                    "hiver": moy_hiver,
                    "printemps": moy_printemps,
                    "ete": moy_ete,
                    "automne": moy_automne,
                    "prcp": moy_prcp,
                    "tsun": moy_tsun
                }
        except:
            continue

    return None  # Si aucune station avec data


# Chargement du DataFrame
df = load_data()

# Vérification de la présence de la colonne contenant le nom de la commune
if "nom_standard" not in df.columns:
    st.error("La colonne 'nom_standard' n'est pas présente dans le DataFrame.")
else:
    # Trier les noms de communes en ordre alphabétique pour faciliter leur recherche dans la selectbox
    communes = sorted(df["nom_standard"].unique())

    st.title("Comparateur de Communes")
    st.markdown("Sélectionnez une commune à gauche et une à droite pour comparer leurs informations et images.")

    # Sélection des communes dans deux colonnes (selectbox intégrée avec saisie possible pour filtrer)
    col_select_left, col_select_right = st.columns(2)
    with col_select_left:
        commune_gauche = st.selectbox("Commune de gauche", communes, key="commune_gauche")
    with col_select_right:
        commune_droite = st.selectbox("Commune de droite", communes, key="commune_droite")

    st.markdown("---")

    # Affichage des informations et images dans deux colonnes
    col_detail_left, col_detail_right = st.columns(2)

    # Détails pour la commune de gauche
    with col_detail_left:
        st.header(f"Détails de {commune_gauche}")
        details_gauche = df[df["nom_standard"] == commune_gauche]
        if not details_gauche.empty:
            row = details_gauche.iloc[0]
            # Affichage de chaque information issue du CSV
            for col_name in details_gauche.columns:
                st.markdown(f"**{col_name}** : {row[col_name]}")
            # Récupérer et afficher l'image via Wikipédia à partir du code INSEE
            code_insee_left = row["code_insee"]
            if code_insee_left:
                with st.spinner("Recherche de l'image..."):
                    title_wiki = get_wikipedia_title_from_insee(code_insee_left)
                    if title_wiki:
                        image_url, city_name, _ = get_wikipedia_thumbnail(title_wiki)
                        if image_url:
                            st.image(image_url, caption=city_name, width=400)
                        else:
                            st.warning("Aucune image trouvée pour cette commune.")
                    else:
                        st.error("Aucune page Wikipédia trouvée pour ce code INSEE.")
        else:
            st.write("Aucune donnée disponible.")

        # Récupération météo
        with st.spinner("Recherche de la météo..."):
            forecast_left = get_weather_forecast(code_insee_left)
            if forecast_left:
                st.subheader("Prévisions météo (prochains jours)")
                for day in forecast_left:
                    st.write(f"📅 {day['date']}")
                    st.write(f"🌦️ {day['weather']}")
                    st.write(f"🌡️ {day['tmin']}°C → {day['tmax']}°C")
                    st.write(f"🌬️ Vent moyen : {day['wind']} km/h")
                    st.write(f"☀️ Ensoleillement : {day['sun_hours']} h")
                    st.markdown("---")
            else:
                st.warning("Pas de données météo disponibles.")

        # Récupération climat
        latitude_left = row["latitude_centre"]
        longitude_left = row["longitude_centre"]

        if pd.notna(latitude_left) and pd.notna(longitude_left):
            with st.spinner("Recherche du climat..."):
                climat_left = get_climate_data(latitude_left, longitude_left)
                if climat_left:
                    st.subheader("Climat (1981–2010)")
                    st.write(f"🌡️ Hiver : {climat_left['hiver']} °C")
                    st.write(f"🌡️ Printemps : {climat_left['printemps']} °C")
                    st.write(f"🌡️ Été : {climat_left['ete']} °C")
                    st.write(f"🌡️ Automne : {climat_left['automne']} °C")
                    st.write(f"🌧️ Précipitations moyennes : {climat_left['prcp']} mm/mois")
                    st.write(f"🌤️ Ensoleillement moyen : {round(climat_left['tsun']/60, 1)} h/jour")
                else:
                    st.warning("Pas de données climatiques disponibles.")


    # Détails pour la commune de droite
    with col_detail_right:
        st.header(f"Détails de {commune_droite}")
        details_droite = df[df["nom_standard"] == commune_droite]
        if not details_droite.empty:
            row = details_droite.iloc[0]
            for col_name in details_droite.columns:
                st.markdown(f"**{col_name}** : {row[col_name]}")
            code_insee_right = row["code_insee"]
            if code_insee_right:
                with st.spinner("Recherche de l'image..."):
                    title_wiki = get_wikipedia_title_from_insee(code_insee_right)
                    if title_wiki:
                        image_url, city_name, _ = get_wikipedia_thumbnail(title_wiki)
                        if image_url:
                            st.image(image_url, caption=city_name, width=400)
                        else:
                            st.warning("Aucune image trouvée pour cette commune.")
                    else:
                        st.error("Aucune page Wikipédia trouvée pour ce code INSEE.")
        else:
            st.write("Aucune donnée disponible.")
        # Récupération météo
        with st.spinner("Recherche de la météo..."):
            forecast_left = get_weather_forecast(code_insee_left)
            if forecast_left:
                st.subheader("Prévisions météo (prochains jours)")
                for day in forecast_left:
                    st.write(f"📅 {day['date']}")
                    st.write(f"🌦️ {day['weather']}")
                    st.write(f"🌡️ {day['tmin']}°C → {day['tmax']}°C")
                    st.write(f"🌬️ Vent moyen : {day['wind']} km/h")
                    st.write(f"☀️ Ensoleillement : {day['sun_hours']} h")
                    st.markdown("---")
            else:
                st.warning("Pas de données météo disponibles.")

        # Récupération climat
        latitude_left = row["latitude_centre"]
        longitude_left = row["longitude_centre"]

        if pd.notna(latitude_left) and pd.notna(longitude_left):
            with st.spinner("Recherche du climat..."):
                climat_left = get_climate_data(latitude_left, longitude_left)
                if climat_left:
                    st.subheader("Climat (1981–2010)")
                    st.write(f"🌡️ Hiver : {climat_left['hiver']} °C")
                    st.write(f"🌡️ Printemps : {climat_left['printemps']} °C")
                    st.write(f"🌡️ Été : {climat_left['ete']} °C")
                    st.write(f"🌡️ Automne : {climat_left['automne']} °C")
                    st.write(f"🌧️ Précipitations moyennes : {climat_left['prcp']} mm/mois")
                    st.write(f"🌤️ Ensoleillement moyen : {round(climat_left['tsun']/60, 1)} h/jour")
                else:
                    st.warning("Pas de données climatiques disponibles.")
