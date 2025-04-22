import streamlit as st
import pandas as pd
import requests
import locale
import requests
# Forcer l'affichage en français
try:
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR')
    except:
        st.warning("⚠️ Impossible de définir la langue française pour les jours.")
# Configuration de la page en mode "wide"
st.set_page_config(page_title="Comparateur de Communes", layout="wide")
# 🔐 Authentification OAuth2
@st.cache_data
def get_pe_token():
    url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"
    data = {
        "grant_type": "client_credentials",
        "client_id": "PAR_comparateurdecommunes_d44d672332727b5c715e2e24ef11865c5ab443fc86b3a073d38e251020046855",
        "client_secret": "885aa9f7ed46b4b9396b013b21f54877f7cbcc8a1c974bad376ec14c6d28416a",
        "scope": "api_offresdemploiv2 o2dsoffre"
    }
    response = requests.post(url, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        st.error("Échec de l'authentification auprès de l'API Pôle Emploi.")
        return None

# 📦 Requête d'offres d'emploi via code postal
@st.cache_data
def get_job_offers(insee_code, token, rayon=10):
    url = "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "commune": insee_code,  # utilise code INSEE ici
        "rayon": rayon,
        "range": "0-5",
    }
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("resultats", [])






# Chargement des données depuis le CSV avec mise en cache
@st.cache_data
def load_data():
    df = pd.read_csv("data/communes_synthetique.csv")
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

@st.cache_data
def load_loyer_data():
    df_loyer = pd.read_csv("data/pred-app-mef-dhup.csv", encoding="latin1", sep=";")
    df_loyer.columns = df_loyer.columns.str.strip()
    df_loyer["INSEE_C"] = df_loyer["INSEE_C"].astype(str).str.strip()

    for col in ["loypredm2", "lwr.IPm2", "upr.IPm2"]:
        df_loyer[col] = df_loyer[col].astype(str).str.replace(",", ".")
        df_loyer[col] = pd.to_numeric(df_loyer[col], errors="coerce")

    return df_loyer




@st.cache_data
def get_loyer_info(insee_code, df_loyer):
    infos = df_loyer[df_loyer["INSEE_C"] == str(insee_code)]
    if infos.empty:
        return None
    else:
        row = infos.iloc[0]
        return {
            "loypredm2": round(row["loypredm2"], 2),
            "lwr": round(row["lwr.IPm2"], 2),
            "upr": round(row["upr.IPm2"], 2),
            "nbobs": int(row["nbobs_com"])
        }

# Chargement des données d'emploi
@st.cache_data
def load_employment_data():
    # Lecture du fichier CSV avec le bon séparateur
    df_emploi = pd.read_csv("data/data.csv", sep=";")
    # Nettoyage des noms de colonnes
    df_emploi.columns = df_emploi.columns.str.strip()
    # Suppression des lignes vides ou de métadonnées
    df_emploi = df_emploi.dropna(subset=['Code'])
    # Conversion des codes en string pour éviter les problèmes de comparaison
    df_emploi['Code'] = df_emploi['Code'].astype(str).str.strip()
    return df_emploi

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



# Chargement du DataFrame
df = load_data()
df_loyer = load_loyer_data()

# Vérification de la présence de la colonne contenant le nom de la commune
if "nom_standard" not in df.columns:
    st.error("La colonne 'nom_standard' n'est pas présente dans le DataFrame.")
else:
    # Trier les noms de communes en ordre alphabétique pour faciliter leur recherche dans la selectbox
    communes = sorted(df["nom_standard"].unique())

    st.title("Comparateur de Communes")
    st.markdown("Sélectionnez une commune à gauche et une à droite pour comparer leurs informations.")

    # Sélection des communes dans deux colonnes (selectbox intégrée avec saisie possible pour filtrer)
    col_select_left, col_select_right = st.columns(2)
    # Prendre automatiquement la première et la deuxième commune
    commune_gauche_defaut = communes[0]
    commune_droite_defaut = communes[1]
    with col_select_left:
        commune_gauche = st.selectbox(
            "Commune de gauche",
            communes,
            index=0,  # Première ville
            key="commune_gauche"
        )

    with col_select_right:
        commune_droite = st.selectbox(
            "Commune de droite",
            communes,
            index=1,  # Deuxième ville
            key="commune_droite"
        )


    st.markdown("---")

    # Affichage des informations et images dans deux colonnes
    col_detail_left, col_detail_right = st.columns(2)

    # Détails pour la commune de gauche
    with col_detail_left:
        st.header(f"🏙️ Détails de {commune_gauche}")
        details_gauche = df[df["nom_standard"] == commune_gauche]

        if not details_gauche.empty:
            row = details_gauche.iloc[0]

            # Deux colonnes pour présentation
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📍 Informations générales")
                st.markdown(f"**Nom** : {row['nom_standard']}")
                st.markdown(f"**Code postal** : {int(row['code_postal']) if not pd.isna(row['code_postal']) else 'Non disponible'}")
                st.markdown(f"**Département** : {row['dep_nom']}")
                st.markdown(f"**Région** : {row['reg_nom']}")

            with col2:
                st.subheader("👥 Démographie")
                st.markdown(f"**Population** : {row['population']:,} habitants")
                st.markdown(f"**Superficie** : {row['superficie_km2']} km²")
                st.markdown(f"**Densité** : {row['grille_densite_texte']}")

            st.markdown("---")

            # Carte de localisation
            st.subheader("🗺️ Localisation sur la carte")
            df_map = pd.DataFrame({
                'lat': [row['latitude_centre']],
                'lon': [row['longitude_centre']]
            })
            col1, col2 = st.columns(2)

            with col1:
                # --- Gestion des communes sans coordonnées ---

                # Vérifier s'il y a des NaN dans lat/lon
                nb_villes_incompletes = df_map["lat"].isna().sum() + df_map["lon"].isna().sum()

                # Supprimer les lignes sans lat/lon pour la carte
                df_map = df_map.dropna(subset=["lat", "lon"])

                # Si certaines communes n'ont pas été affichées, prévenir
                if nb_villes_incompletes > 0:
                    st.warning(f"⚠️ Cette ville n'a pas pu être affichée car ces coordonnées sont manquantes.")

                # --- Afficher la carte ---
                st.map(df_map, zoom=6)


            st.markdown("---")

            # Lien Wikipedia si disponible
            if pd.notna(row['url_wikipedia']):
                st.markdown(f"[🔗 Voir sur Wikipédia]({row['url_wikipedia']})")

            # Image de la ville
            code_insee_left = row["code_insee"]
            if code_insee_left:
                with st.spinner("🔎 Recherche de l'image..."):
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
            st.write("Aucune donnée disponible pour cette commune.")



        # Récupération météo
        with st.spinner("Recherche de la météo..."):
            forecast_left = get_weather_forecast(code_insee_left)
            if forecast_left:
                st.subheader("Prévisions météo (prochains jours)")
                df_meteo_left = pd.DataFrame(forecast_left)
                df_meteo_left = df_meteo_left.rename(columns={
                    "date": "Date",
                    "weather": "Météo",
                    "tmin": "Min (°C)",
                    "tmax": "Max (°C)",
                    "wind": "Vent (km/h)",
                    "sun_hours": "Ensoleillement (h)"
                })
                # 🆕 Reformater la colonne Date
                df_meteo_left["Date"] = pd.to_datetime(df_meteo_left["Date"]).dt.strftime('%A')
                df_meteo_left.loc[0, "Date"] = "Aujourd'hui"
                st.table(df_meteo_left)
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
                    st.write(f"🌡️ Hiver : {climat_left['hiver']} °C" if climat_left and climat_left['hiver'] is not None else "🌡️ Hiver : Donnée indisponible")
                    st.write(f"🌡️ Printemps : {climat_left['printemps']} °C" if climat_left and climat_left['printemps'] is not None else "🌡️ Printemps : Donnée indisponible")
                    st.write(f"🌡️ Été : {climat_left['ete']} °C" if climat_left and climat_left['ete'] is not None else "🌡️ Été : Donnée indisponible")
                    st.write(f"🌡️ Automne : {climat_left['automne']} °C" if climat_left and climat_left['automne'] is not None else "🌡️ Automne : Donnée indisponible")
                    st.write(f"🌧️ Précipitations moyennes : {climat_left['prcp']} mm/mois" if climat_left and climat_left['prcp'] is not None else "🌧️ Précipitations moyennes : Donnée indisponible")
                    st.write(f"🌤️ Ensoleillement moyen : {round(climat_left['tsun']/60, 1)} h/mois" if climat_left and climat_left['tsun'] is not None else "🌤️ Ensoleillement moyen : Donnée indisponible")
                else:
                    st.warning("Pas de données climatiques disponibles.")
        # Affichage des données logement
        loyer_left = get_loyer_info(code_insee_left, df_loyer)
        if loyer_left:
            st.subheader("Loyer moyen (T3 2023)")
            st.write(f"🏠 Prix moyen au m² : {loyer_left['loypredm2']} €/m²")
            st.write(f"📏 Intervalle estimé : {loyer_left['lwr']} € - {loyer_left['upr']} € /m²")
            st.write(f"📈 Nombre d'annonces analysées : {loyer_left['nbobs']}")
            if loyer_left['nbobs'] < 30:
                st.warning("⚠️ Fiabilité faible : moins de 30 observations.")
        else:
            st.warning("Pas de données de loyer disponibles pour cette commune.")

        # Offres d'emploi récentes
        token_pe = get_pe_token()
        if token_pe and pd.notna(row['code_postal']):
            st.subheader("🧳 Offres d'emploi récentes")
            code_insee = row["code_insee"]
            offres = get_job_offers(code_insee, token_pe)
            if offres:
                for offre in offres:
                    st.markdown(f"**{offre.get('intitule', 'Sans titre')}**")

                    # 📍 Lieu
                    lieu = offre.get("lieuTravail", {}).get("libelle", "Lieu non précisé")
                    st.write(f"📍 {lieu}")

                    # 🗓️ Date
                    date_creation = offre.get("dateCreation")
                    if date_creation:
                        st.write(f"🗓️ Publiée le : {date_creation[:10]}")

                    # 🎓 Alternance
                    if offre.get("alternance", False):
                        st.write("🎓 Offre en alternance")

                    # 🔗 Lien vers l'offre
                    url = offre.get("origineOffre", {}).get("url")
                    url_origine = offre.get("origineOffre", {}).get("urlOrigine")

                    if url:
                        st.markdown(f"[🔗 Voir l'offre (France Travail)]({url})")
                    elif url_origine:
                        st.markdown(f"[🔗 Voir l'offre (partenaire)]({url_origine})")
                    else:
                        st.write("❌ Aucun lien vers l’offre fourni")

                    st.markdown("---")


            else:
                st.info("Aucune offre récente trouvée dans cette zone.")
                st.write("Debug - Code postal : ", str(int(row["code_postal"])))
                st.write("Token : ", token_pe)



######################################################################################################################################
######################################################################################################################################
######################################################################################################################################

    # Détails pour la commune de droite
    with col_detail_right:
        st.header(f"🏙️ Détails de {commune_droite}")
        details_droite = df[df["nom_standard"] == commune_droite]

        if not details_droite.empty:
            row = details_droite.iloc[0]

            # Deux colonnes pour présentation
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📍 Informations générales")
                st.markdown(f"**Nom** : {row['nom_standard']}")
                st.markdown(f"**Code postal** : {int(row['code_postal']) if not pd.isna(row['code_postal']) else 'Non disponible'}")
                st.markdown(f"**Département** : {row['dep_nom']}")
                st.markdown(f"**Région** : {row['reg_nom']}")

            with col2:
                st.subheader("👥 Démographie")
                st.markdown(f"**Population** : {row['population']:,} habitants")
                st.markdown(f"**Superficie** : {row['superficie_km2']} km²")
                st.markdown(f"**Densité** : {row['grille_densite_texte']}")

            st.markdown("---")

            # Carte de localisation
            st.subheader("🗺️ Localisation sur la carte")
            df_map = pd.DataFrame({
                'lat': [row['latitude_centre']],
                'lon': [row['longitude_centre']]
            })
            col1, col2 = st.columns(2)

            with col1:
                # --- Gestion des communes sans coordonnées ---

                # Vérifier s'il y a des NaN dans lat/lon
                nb_villes_incompletes = df_map["lat"].isna().sum() + df_map["lon"].isna().sum()

                # Supprimer les lignes sans lat/lon pour la carte
                df_map = df_map.dropna(subset=["lat", "lon"])

                # Si certaines communes n'ont pas été affichées, prévenir
                if nb_villes_incompletes > 0:
                    st.warning(f"⚠️ Cette ville n'a pas pu être affichée car ces coordonnées sont manquantes.")

                # --- Afficher la carte ---
                st.map(df_map, zoom=6)



            st.markdown("---")

            # Lien Wikipedia si disponible
            if pd.notna(row['url_wikipedia']):
                st.markdown(f"[🔗 Voir sur Wikipédia]({row['url_wikipedia']})")

            # Image de la ville
            code_insee_right = row["code_insee"]
            if code_insee_right:
                with st.spinner("🔎 Recherche de l'image..."):
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
            st.write("Aucune donnée disponible pour cette commune.")


        # Récupération météo
        with st.spinner("Recherche de la météo..."):
            forecast_right = get_weather_forecast(code_insee_right)
            if forecast_right:
                st.subheader("Prévisions météo (prochains jours)")
                df_meteo_right = pd.DataFrame(forecast_right)
                df_meteo_right = df_meteo_right.rename(columns={
                    "date": "Date",
                    "weather": "Météo",
                    "tmin": "Min (°C)",
                    "tmax": "Max (°C)",
                    "wind": "Vent (km/h)",
                    "sun_hours": "Ensoleillement (h)"
                })
                # 🆕 Reformater la colonne Date
                df_meteo_right["Date"] = pd.to_datetime(df_meteo_right["Date"]).dt.strftime('%A')
                df_meteo_right.loc[0, "Date"] = "Aujourd'hui"
                st.table(df_meteo_right)
            else:
                st.warning("Pas de données météo disponibles.")

        # Récupération climat
        latitude_right = row["latitude_centre"]
        longitude_right = row["longitude_centre"]

        if pd.notna(latitude_right) and pd.notna(longitude_right):
            with st.spinner("Recherche du climat..."):
                climat_right = get_climate_data(latitude_right, longitude_right)
                if climat_right:
                    st.subheader("Climat (1981–2010)")
                    st.write(f"🌡️ Hiver : {climat_right['hiver']} °C" if climat_right and climat_right['hiver'] is not None else "🌡️ Hiver : Donnée indisponible")
                    st.write(f"🌡️ Printemps : {climat_right['printemps']} °C" if climat_right and climat_right['printemps'] is not None else "🌡️ Printemps : Donnée indisponible")
                    st.write(f"🌡️ Été : {climat_right['ete']} °C" if climat_right and climat_right['ete'] is not None else "🌡️ Été : Donnée indisponible")
                    st.write(f"🌡️ Automne : {climat_right['automne']} °C" if climat_right and climat_right['automne'] is not None else "🌡️ Automne : Donnée indisponible")
                    st.write(f"🌧️ Précipitations moyennes : {climat_right['prcp']} mm/mois" if climat_right and climat_right['prcp'] is not None else "🌧️ Précipitations moyennes : Donnée indisponible")
                    st.write(f"🌤️ Ensoleillement moyen : {round(climat_right['tsun']/60, 1)} h/mois" if climat_right and climat_right['tsun'] is not None else "🌤️ Ensoleillement moyen : Donnée indisponible")
                else:
                    st.warning("Pas de données climatiques disponibles.")

        loyer_right = get_loyer_info(code_insee_right, df_loyer)
        if loyer_right:
            st.subheader("Loyer moyen (T3 2023)")
            st.write(f"🏠 Prix moyen au m² : {loyer_right['loypredm2']} €/m²")
            st.write(f"📏 Intervalle estimé : {loyer_right['lwr']} € - {loyer_right['upr']} € /m²")
            st.write(f"📈 Nombre d'annonces analysées : {loyer_right['nbobs']}")
            if loyer_right['nbobs'] < 30:
                st.warning("⚠️ Fiabilité faible : moins de 30 observations.")


        # Offres d'emploi récentes
        token_pe = get_pe_token()
        if token_pe and pd.notna(row['code_postal']):
            st.subheader("🧳 Offres d'emploi récentes")
            code_insee = row["code_insee"]
            offres = get_job_offers(code_insee, token_pe)

            if offres:
                for offre in offres:
                    st.markdown(f"**{offre.get('intitule', 'Sans titre')}**")

                    # 📍 Lieu
                    lieu = offre.get("lieuTravail", {}).get("libelle", "Lieu non précisé")
                    st.write(f"📍 {lieu}")

                    # 🗓️ Date
                    date_creation = offre.get("dateCreation")
                    if date_creation:
                        st.write(f"🗓️ Publiée le : {date_creation[:10]}")

                    # 🎓 Alternance
                    if offre.get("alternance", False):
                        st.write("🎓 Offre en alternance")

                    # 🔗 Lien vers l'offre
                    url = offre.get("origineOffre", {}).get("url")
                    url_origine = offre.get("origineOffre", {}).get("urlOrigine")

                    if url:
                        st.markdown(f"[🔗 Voir l'offre (France Travail)]({url})")
                    elif url_origine:
                        st.markdown(f"[🔗 Voir l'offre (partenaire)]({url_origine})")
                    else:
                        st.write("❌ Aucun lien vers l’offre fourni")

                    st.markdown("---")

            else:
                st.info("Aucune offre récente trouvée dans cette zone.")
                st.write("Debug - Code postal : ", str(int(row["code_postal"])))
                st.write("Token : ", token_pe)

            
 # Section de comparaison des données d'emploi
st.markdown("---")
st.header("Comparaison des données d'emploi")

df = load_data()
df_emploi = load_employment_data()

# Nettoyage et standardisation des colonnes pour éviter les erreurs
df_emploi.columns = df_emploi.columns.str.strip()

# Affichage des colonnes pour debug (désactive si tout fonctionne)
# st.write("Colonnes dans data.csv :", df_emploi.columns.tolist())

# On cherche la colonne qui contient les codes INSEE
possible_code_col = [col for col in df_emploi.columns if "code" in col.lower()]
code_col = possible_code_col[0] if possible_code_col else None

if code_col is None:
    st.error("Impossible de trouver la colonne contenant les codes INSEE dans le fichier data.csv.")
else:
    # Sélection des lignes pour les deux communes
    emploi_gauche = df_emploi[df_emploi[code_col].astype(str).str.strip() == str(code_insee_left)]
    emploi_droite = df_emploi[df_emploi[code_col].astype(str).str.strip() == str(code_insee_right)]

    # Vérifie si les deux communes sont présentes
    if not emploi_gauche.empty and not emploi_droite.empty:
        # Tentative de détection automatique des colonnes utiles
        try:
            pop_col = [col for col in df_emploi.columns if "population municipale" in col.lower()][0]
            nb_emplois_col = [col for col in df_emploi.columns if "emplois au lieu de travail" in col.lower()][0]
            part_salaries_col = [col for col in df_emploi.columns if "emplois sal" in col.lower()][0]
            

            compare_df = pd.DataFrame({
                'Commune': [commune_gauche, commune_droite],
                'Population': [
                    int(str(emploi_gauche.iloc[0][pop_col]).replace(" ", "").replace(",", "")),
                    int(str(emploi_droite.iloc[0][pop_col]).replace(" ", "").replace(",", ""))
                ],
                '% emplois salariés': [
                    float(str(emploi_gauche.iloc[0][part_salaries_col]).replace(",", ".").replace("%", "").strip()),
                    float(str(emploi_droite.iloc[0][part_salaries_col]).replace(",", ".").replace("%", "").strip())
                ],
                'Nb emplois': [
                    int(str(emploi_gauche.iloc[0][nb_emplois_col]).replace(" ", "").replace(",", "")),
                    int(str(emploi_droite.iloc[0][nb_emplois_col]).replace(" ", "").replace(",", ""))
                ]
            })

            # Calcul du ratio emplois/population
            compare_df['Emplois pour 1000 hab.'] = (compare_df['Nb emplois'] / compare_df['Population']) * 1000

            # Affichage des données
            st.dataframe(compare_df.set_index("Commune").T)


            # ---------- GRAPHIQUE Plotly interactif ----------
            import plotly.express as px

            # Graphique 3 : Population
            fig3 = px.bar(compare_df, x="Commune", y="Population", color="Commune",
                        title="Population municipale (2022)", text="Population")
            st.plotly_chart(fig3, use_container_width=True)

            # Graphique 1 : Nombre d'emplois
            fig1 = px.bar(compare_df, x="Commune", y="Nb emplois", color="Commune",
                        title="Nombre total d'emplois (2021)", text="Nb emplois")
            st.plotly_chart(fig1, use_container_width=True)

            # Graphique 2 : Pourcentage d'emplois salariés
            fig2 = px.bar(compare_df, x="Commune", y="% emplois salariés", color="Commune",
                        title="Part des emplois salariés (%)", text="% emplois salariés")
            fig2.update_yaxes(range=[0, 100])
            st.plotly_chart(fig2, use_container_width=True)


            compare_df["Emplois pour 1000 hab. arrondis"] = compare_df["Emplois pour 1000 hab."].round(0).astype(int)
            fig4 = px.bar(compare_df, x="Commune", y="Emplois pour 1000 hab. arrondis", color="Commune",
              title="Emplois pour 1000 habitants", 
              text="Emplois pour 1000 hab. arrondis")
            st.plotly_chart(fig4, use_container_width=True)


        except Exception as e:
            st.error(f"Erreur lors de l'analyse des données d'emploi : {e}")
    else:
        st.warning("Données d'emploi manquantes pour une ou les deux communes.")



