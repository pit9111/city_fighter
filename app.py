import streamlit as st
import pandas as pd
import requests

import pydeck as pdk
from datetime import datetime
# 🔐 Authentification OAuth2

# Configuration de la page en mode "wide"
st.set_page_config(page_title="Comparateur de Communes", layout="wide")

@st.cache_data
def get_pe_token(ttl=3500):
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
        "commune": insee_code,
        "rayon": rayon,
        "range": "0-5",
    }

    response = requests.get(url, headers=headers, params=params)

    try:
        data = response.json()
        return data.get("resultats", [])
    except ValueError:
        st.warning("❌ Réponse invalide reçue de l'API Pôle Emploi.")
        st.text(f"Statut: {response.status_code}")
        st.text(f"Contenu brut: {response.text[:300]}...")  # Affiche les premiers caractères de la réponse
        return []



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
        mois_francais = {
            1: "janvier", 2: "février", 3: "mars", 4: "avril",
            5: "mai", 6: "juin", 7: "juillet", 8: "août",
            9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
        }
        jours_francais = {
            0: "lundi", 1: "mardi", 2: "mercredi", 3: "jeudi",
            4: "vendredi", 5: "samedi", 6: "dimanche"
        }

        forecasts = []
        for item in data['forecast'][:4]:  # ← 4 jours
            date_obj = datetime.strptime(item['datetime'][:10], "%Y-%m-%d")
            date_fr = f"{jours_francais[date_obj.weekday()]} {date_obj.day} {mois_francais[date_obj.month]} {date_obj.year}"
            forecasts.append({
                "date": date_fr,
                "weather": weather_codes.get(item['weather'], f"Code {item['weather']}"),
                "tmin": item['tmin'],
                "tmax": item['tmax'],
                "wind": item['wind10m'],
                "sun_hours": item['sun_hours']
            })

        return forecasts  # ✅ return après la boucle

    else:
        return None

# Fonction pour récupérer les normales climatiques d'une commune
@st.cache_data
def get_climate_data(latitude, longitude):
    import http.client
    import json

    conn = http.client.HTTPSConnection("meteostat.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "a7fc9e231fmshc0a28b3edb37cc1p147917jsn848c388c60a8",
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
    grandes_villes = {
        "Paris": "751",
        "Marseille": "132",
        "Lyon": "693"
    }

    insee_code_str = str(insee_code)

    # Vérifie si c'est une grande ville
    for ville, prefixe in grandes_villes.items():
        if insee_code_str.startswith(prefixe):
            infos = df_loyer[df_loyer["INSEE_C"].str.startswith(prefixe)]
            if infos.empty:
                return None
            else:
                # ⚡ Ici on prend la moyenne pour être logique
                moy_loypredm2 = round(infos["loypredm2"].mean(), 2)
                moy_lwr = round(infos["lwr.IPm2"].mean(), 2)
                moy_upr = round(infos["upr.IPm2"].mean(), 2)
                nbobs_total = int(infos["nbobs_com"].sum())

                return {
                    "loypredm2": moy_loypredm2,
                    "lwr": moy_lwr,
                    "upr": moy_upr,
                    "nbobs": nbobs_total
                }

    # 🔹 Cas normal pour les autres villes
    infos = df_loyer[df_loyer["INSEE_C"] == insee_code_str]
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

@st.cache_data
def load_culture_data():
    df_culture = pd.read_csv("data/base_culture.csv", sep=";", encoding="utf-8", low_memory=False)
    df_culture.columns = df_culture.columns.str.strip()
    df_culture["code_insee"] = df_culture["code_insee"].astype(str).str.zfill(5)
    df_culture = df_culture.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
    df_culture = df_culture.dropna(subset=["latitude", "longitude"])  # supprime les lignes sans coord
    return df_culture

@st.cache_data
def load_formation_data():
    df_form = pd.read_csv("data/base_formation.csv", sep=";", encoding="utf-8", low_memory=False)
    df_form.columns = df_form.columns.str.strip()

    # Séparation de latitude/longitude
    df_form[['latitude', 'longitude']] = df_form["Localisation"].str.split(",", expand=True).astype(float)
    df_form = df_form.dropna(subset=["latitude", "longitude"])
    return df_form

# Chargement des données
df = load_data()
df_loyer = load_loyer_data()
df_emploi = load_employment_data()

# Interface utilisateur
st.title("Comparateur de Communes")
st.markdown("Sélectionnez une commune à gauche et une à droite pour comparer leurs informations.")

with st.sidebar:
    st.title("🧭 Paramètres")
    communes = sorted(df["nom_standard"].unique())
    commune_gauche_defaut = communes[0]
    commune_droite_defaut = communes[1]
    commune_gauche = st.selectbox("Commune de gauche", communes, index=0, key="commune_gauche")
    commune_droite = st.selectbox("Commune de droite", communes, index=1, key="commune_droite")

    
    st.markdown("---")
    st.markdown("**👥 Connectez-vous avec nous sur LinkedIn :**")
    st.markdown("[Daniel Da Silva](https://www.linkedin.com/in/daniel-da-silva-50368a268/)")
    st.markdown("[Furkan Narin](https://www.linkedin.com/in/furkan-narin/)")
    st.markdown("[Léo-Paul Houitte](https://www.linkedin.com/in/l%C3%A9o-paul-houitte/)")



# Récupération des données
data_gauche = df[df["nom_standard"] == commune_gauche].iloc[0]
data_droite = df[df["nom_standard"] == commune_droite].iloc[0]

code_insee_left = data_gauche["code_insee"]
code_insee_right = data_droite["code_insee"]

# Création des onglets
onglet1, onglet2, onglet3, onglet4, onglet5, onglet6 = st.tabs(["📊 Données générales", "💼 Emploi", "🏠 Logement", "🌦️ Météo", "🎭 Culture", "🎓 Formation"])

# Onglet 1: Données générales
with onglet1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.header(f"🏙️ {commune_gauche}")
        st.subheader("📍 Informations générales")
        st.markdown(f"**Nom** : {data_gauche['nom_standard']}")
        st.markdown(f"**Code postal** : {int(data_gauche['code_postal']) if not pd.isna(data_gauche['code_postal']) else 'Non disponible'}")
        st.markdown(f"**Département** : {data_gauche['dep_nom']}")
        st.markdown(f"**Région** : {data_gauche['reg_nom']}")
        
        st.subheader("👥 Démographie")
        st.markdown(f"**Population** : {data_gauche['population']:,} habitants")
        st.markdown(f"**Superficie** : {data_gauche['superficie_km2']} km²")
        st.markdown(f"**Catégorie urbaine** : {data_gauche['grille_densite_texte']}")

                # Carte de localisation
        st.subheader("🗺️ Localisation")
        df_map = pd.DataFrame({
            'lat': [data_gauche['latitude_centre']],
            'lon': [data_gauche['longitude_centre']]
        })
        nb_villes_incompletes = df_map["lat"].isna().sum() + df_map["lon"].isna().sum()
        df_map = df_map.dropna(subset=["lat", "lon"])

        if nb_villes_incompletes > 0:
            st.warning(f"⚠️ Cette ville n'a pas pu être affichée car ces coordonnées sont manquantes.")

        st.map(df_map, zoom=6)
        
        # Image Wikipedia
        title_wiki = get_wikipedia_title_from_insee(code_insee_left)
        if title_wiki:
            image_url, city_name, extract = get_wikipedia_thumbnail(title_wiki)
            if image_url:
                st.image(image_url, caption=city_name, width=300)
            if extract:
                st.markdown(f"**Description** : {extract}")
            
            # 🔗 Ajout du lien vers Wikipédia
            st.markdown(f"[🔗 Voir l'article Wikipédia](https://fr.wikipedia.org/wiki/{title_wiki})")
        

                
        
        
    
    with col2:
        st.header(f"🏙️ {commune_droite}")
        st.subheader("📍 Informations générales")
        st.markdown(f"**Nom** : {data_droite['nom_standard']}")
        st.markdown(f"**Code postal** : {int(data_droite['code_postal']) if not pd.isna(data_droite['code_postal']) else 'Non disponible'}")
        st.markdown(f"**Département** : {data_droite['dep_nom']}")
        st.markdown(f"**Région** : {data_droite['reg_nom']}")
        
        st.subheader("👥 Démographie")
        st.markdown(f"**Population** : {data_droite['population']:,} habitants")
        st.markdown(f"**Superficie** : {data_droite['superficie_km2']} km²")
        st.markdown(f"**Catégorie urbaine** : {data_droite['grille_densite_texte']}")

                # Carte de localisation
        st.subheader("🗺️ Localisation")
        df_map = pd.DataFrame({
            'lat': [data_droite['latitude_centre']],
            'lon': [data_droite['longitude_centre']]
        })
        nb_villes_incompletes = df_map["lat"].isna().sum() + df_map["lon"].isna().sum()
        df_map = df_map.dropna(subset=["lat", "lon"])

        if nb_villes_incompletes > 0:
            st.warning(f"⚠️ Cette ville n'a pas pu être affichée car ces coordonnées sont manquantes.")

        st.map(df_map, zoom=6)
        
        # Image Wikipedia
        # Image Wikipedia
        title_wiki = get_wikipedia_title_from_insee(code_insee_right)
        if title_wiki:
            image_url, city_name, extract = get_wikipedia_thumbnail(title_wiki)
            if image_url:
                st.image(image_url, caption=city_name, width=300)
            if extract:
                st.markdown(f"**Description** : {extract}")
            
            # 🔗 Ajout du lien vers Wikipédia
            st.markdown(f"[🔗 Voir l'article Wikipédia](https://fr.wikipedia.org/wiki/{title_wiki})")

        

# Onglet 2: Emploi
with onglet2:
    st.header("Comparaison des données d'emploi")
    
    # Nettoyage et standardisation des colonnes pour éviter les erreurs
    df_emploi.columns = df_emploi.columns.str.strip()

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

                # Graphiques Plotly interactifs
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

                st.markdown("---")
                st.markdown("**Sources de données :** [Statistiques locales INSEE](https://statistiques-locales.insee.fr/#c=home)")


            except Exception as e:
                st.error(f"Erreur lors de l'analyse des données d'emploi : {e}")
            
            # Section API Pôle Emploi
            st.header("🧳 Offres d'emploi récentes")
            token_pe = get_pe_token()
            if token_pe:
                col_emploi1, col_emploi2 = st.columns(2)
                
                with col_emploi1:
                    st.subheader(f"{commune_gauche}")
                    offres = get_job_offers(code_insee_left, token_pe)
                    if offres:
                        for offre in offres:
                            st.markdown(f"**{offre.get('intitule', 'Sans titre')}**")
                            lieu = offre.get("lieuTravail", {}).get("libelle", "Lieu non précisé")
                            st.write(f"📍 {lieu}")
                            date_creation = offre.get("dateCreation")
                            if date_creation:
                                st.write(f"🗓️ Publiée le : {date_creation[:10]}")
                            if offre.get("alternance", False):
                                st.write("🎓 Offre en alternance")
                            url = offre.get("origineOffre", {}).get("url")
                            url_origine = offre.get("origineOffre", {}).get("urlOrigine")
                            if url:
                                st.markdown(f"[🔗 Voir l'offre (France Travail)]({url})")
                            elif url_origine:
                                st.markdown(f"[🔗 Voir l'offre (partenaire)]({url_origine})")
                            st.markdown("---")
                    else:
                        st.info("Aucune offre récente trouvée dans cette zone.")
                
                with col_emploi2:
                    st.subheader(f"{commune_droite}")
                    offres = get_job_offers(code_insee_right, token_pe)
                    if offres:
                        for offre in offres:
                            st.markdown(f"**{offre.get('intitule', 'Sans titre')}**")
                            lieu = offre.get("lieuTravail", {}).get("libelle", "Lieu non précisé")
                            st.write(f"📍 {lieu}")
                            date_creation = offre.get("dateCreation")
                            if date_creation:
                                st.write(f"🗓️ Publiée le : {date_creation[:10]}")
                            if offre.get("alternance", False):
                                st.write("🎓 Offre en alternance")
                            url = offre.get("origineOffre", {}).get("url")
                            url_origine = offre.get("origineOffre", {}).get("urlOrigine")
                            if url:
                                st.markdown(f"[🔗 Voir l'offre (France Travail)]({url})")
                            elif url_origine:
                                st.markdown(f"[🔗 Voir l'offre (partenaire)]({url_origine})")
                            st.markdown("---")

                            st.markdown("---")
                            st.markdown("**Sources de données :** [API Offres d'emploi - France Travail (ex-Pôle Emploi)](https://www.data.gouv.fr/fr/dataservices/api-offres-demploi/)")

                    else:
                        st.info("Aucune offre récente trouvée dans cette zone.")
            else:
                st.error("Impossible de se connecter à l'API Pôle Emploi")
        else:
            st.warning("Données d'emploi manquantes pour une ou les deux communes.")


def afficher_loyer(nom_commune, loyer_info):
    if not loyer_info:
        st.warning(f"Pas de données de loyer disponibles pour {nom_commune}.")
        return

    couleur = "#f0f9ff" if loyer_info["nbobs"] >= 30 else "#fff5e6"
    message_fiabilite = (
        "<p style='text-align:center; color: red;'>⚠️ Fiabilité faible : moins de 30 observations.</p>"
        if loyer_info["nbobs"] < 30 else ""
    )

    st.markdown(f"""
    <div style="border: 1px solid #CCC; border-radius: 12px; padding: 20px; background-color: {couleur}; margin-bottom: 20px;">
        <h3 style="text-align:center;">🏠 {nom_commune}</h3>
        <p style="font-size: 26px; text-align:center;"><b>💶 Loyer : {loyer_info['loypredm2']} € / m²</b></p>
        <p style="text-align:center; color: #666;">📏 Intervalle estimé : {loyer_info['lwr']} € – {loyer_info['upr']} € / m²</p>
        <p style="text-align:center; color: #999;">📊 {loyer_info['nbobs']} annonces analysées</p>
        {message_fiabilite}
    </div>
    """, unsafe_allow_html=True)

# Onglet 3: Logement
with onglet3:
    col1, col2 = st.columns(2)


    with col1:
        loyer_left = get_loyer_info(code_insee_left, df_loyer)
        afficher_loyer(commune_gauche, loyer_left)

    with col2:
        loyer_right = get_loyer_info(code_insee_right, df_loyer)
        afficher_loyer(commune_droite, loyer_right)


# Onglet 4: Météo
with onglet4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.header(f"🌦️ Météo - {commune_gauche}")
        
        # Prévisions météo
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


                df_meteo_left.loc[0, "Date"] = "Aujourd'hui"
                # Emoji météo simplifié
                def emoji_meteo(description):
                    if "Soleil" in description:
                        return "☀️"
                    elif "nuageux" in description.lower():
                        return "⛅"
                    elif "pluie" in description.lower():
                        return "🌧️"
                    elif "neige" in description.lower():
                        return "❄️"
                    elif "orage" in description.lower():
                        return "⛈️"
                    else:
                        return "⛅"

                # Colonnes pour chaque jour
                cols = st.columns(len(df_meteo_left))

                for i, jour in df_meteo_left.iterrows():
                    with cols[i]:
                        st.markdown(
                            f"""
                            <div style="border:1px solid #DDD; border-radius:10px; padding:15px; margin-bottom:10px; background-color:#f9f9f9;">
                                <h4 style="text-align:center;">{jour['Date']}</h4>
                                <p style="font-size:40px; text-align:center;">{emoji_meteo(jour['Météo'])}</p>
                                <p style="text-align:center;"><b>{jour['Météo']}</b></p>
                                <p>🌡️ Min : {jour['Min (°C)']}°C</p>
                                <p>🌡️ Max : {jour['Max (°C)']}°C</p>
                                <p>💨 Vent : {jour['Vent (km/h)']} km/h</p>
                                <p>☀️ Ensoleillement : {jour['Ensoleillement (h)']} h</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            else:
                st.warning("Pas de données météo disponibles.")
        
        # Climat
        latitude_left = data_gauche["latitude_centre"]
        longitude_left = data_gauche["longitude_centre"]

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
    
    with col2:
        st.header(f"🌦️ Météo - {commune_droite}")
        
        # Prévisions météo
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
                
                df_meteo_right.loc[0, "Date"] = "Aujourd'hui"
                def emoji_meteo(description):
                    if "Soleil" in description:
                        return "☀️"
                    elif "nuageux" in description.lower():
                        return "⛅"
                    elif "pluie" in description.lower():
                        return "🌧️"
                    elif "neige" in description.lower():
                        return "❄️"
                    elif "orage" in description.lower():
                        return "⛈️"
                    else:
                        return "⛅"

                # Colonnes pour chaque jour
                cols = st.columns(len(df_meteo_left))

                for i, jour in df_meteo_left.iterrows():
                    with cols[i]:
                        st.markdown(
                            f"""
                            <div style="border:1px solid #DDD; border-radius:10px; padding:15px; margin-bottom:10px; background-color:#f9f9f9;">
                                <h4 style="text-align:center;">{jour['Date']}</h4>
                                <p style="font-size:40px; text-align:center;">{emoji_meteo(jour['Météo'])}</p>
                                <p style="text-align:center;"><b>{jour['Météo']}</b></p>
                                <p>🌡️ Min : {jour['Min (°C)']}°C</p>
                                <p>🌡️ Max : {jour['Max (°C)']}°C</p>
                                <p>💨 Vent : {jour['Vent (km/h)']} km/h</p>
                                <p>☀️ Ensoleillement : {jour['Ensoleillement (h)']} h</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
            else:
                st.warning("Pas de données météo disponibles.")
        
        # Climat
        latitude_right = data_droite["latitude_centre"]
        longitude_right = data_droite["longitude_centre"]

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


with onglet5:
    st.header("🎭 Équipements culturels")

    df_culture = load_culture_data()

    def filtrer_par_insee(df, code_insee, commune_nom):
        grandes_villes = {
            "Paris": "751",
            "Marseille": "13055",
            "Lyon": "69123"
        }

        for ville, prefixe in grandes_villes.items():
            if ville.lower() in commune_nom.lower():
                return df[df["code_insee"].str.startswith(prefixe)]
        
        return df[df["code_insee"] == str(code_insee)]
    
    # Filtrage par commune
    lieux_gauche = filtrer_par_insee(df_culture, code_insee_left, commune_gauche)
    lieux_droite = filtrer_par_insee(df_culture, code_insee_right, commune_droite)

    st.markdown("#### Filtrer par type d’équipement")
    search_culture = st.text_input("Tapez un ou plusieurs mots-clé(s) séparés par une virgule (ex: musée, cinéma, bibliothèque)", value="")

    if search_culture:
        keywords_culture = [kw.strip() for kw in search_culture.split(",") if kw.strip()]
        mask_culture = df_culture["Type équipement ou lieu"].apply(lambda x: any(kw.lower() in str(x).lower() for kw in keywords_culture))
        df_culture_filtered = df_culture[mask_culture]
    else:
        df_culture_filtered = df_culture.copy()


    col1, col2 = st.columns(2)

    def show_culture_map(df, nom_commune):
        if df.empty:
            st.info(f"Aucun équipement culturel trouvé pour {nom_commune}.")
            return

        st.markdown(f"### {nom_commune} ({len(df)} lieu(x))")

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[longitude, latitude]',
            get_radius=100,
            get_color=[255, 100, 100],  # Rouge doux
            pickable=True,
        )

        tooltip = {
            "html": "<b>{Nom}</b><br/>{Type équipement ou lieu}<br/>{Adresse}",
            "style": {"backgroundColor": "white", "color": "black"}
        }

        view_state = pdk.ViewState(
            latitude=df["latitude"].mean(),
            longitude=df["longitude"].mean(),
            zoom=11,
            pitch=0,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style="mapbox://styles/mapbox/light-v9"  # ✅ Fond gris clair
        ))

        # ✅ Tableau sans index
        st.dataframe(
            df[["Nom", "Type équipement ou lieu", "Adresse", "Domaine"]].dropna(),
            use_container_width=True,
            hide_index=True  # ⚡ Solution Streamlit 1.30+ pour cacher index
        )

        st.markdown("---")
        st.markdown("**Sources de données :** [Base des lieux et équipements culturels - BASILIC](https://www.data.gouv.fr/fr/datasets/base-des-lieux-et-equipements-culturels-basilic/)")



    with col1:
        show_culture_map(lieux_gauche, commune_gauche)

    with col2:
        show_culture_map(lieux_droite, commune_droite)





with onglet6:
        st.header("🎓 Formations disponibles dans chaque commune")

        df_form = load_formation_data()

    # 🎯 Saisie libre pour filtrer le type de formation
        st.markdown("#### Filtrer par type de formation")
        search_type = st.text_input("Tapez un ou plusieurs mot-clé(s) du type de formation (ex: Licence, BTS, BUT)", value="")

        if search_type:
            keywords = [kw.strip() for kw in search_type.split(",") if kw.strip()]
            mask = df_form["Types de formation"].apply(lambda x: any(kw.lower() in str(x).lower() for kw in keywords))
            df_form_filtered = df_form[mask]
        else:
            df_form_filtered = df_form.copy()


        # Sélection des communes
        villes_gauche = df_form_filtered[df_form_filtered["Commune"].str.lower() == commune_gauche.lower()]
        villes_droite = df_form_filtered[df_form_filtered["Commune"].str.lower() == commune_droite.lower()]

        col1, col2 = st.columns(2)

        # 📍 Fonction carte + tableau
        def show_formation_map(df, nom_commune):
            if df.empty:
                st.info(f"Aucune formation trouvée pour {nom_commune}.")
                return

            st.markdown(f"### {nom_commune} ({len(df)} formation(s))")

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position='[longitude, latitude]',
                get_radius=100,
                get_color=[0, 100, 200],  # Bleu
                pickable=True,
            )

            tooltip = {
                "html": "<b>{Nom de l'établissement}</b><br/>{Nom long de la formation}<br/><a href='{Lien vers la fiche formation}' target='_blank'>Voir fiche</a>",
                "style": {"backgroundColor": "white", "color": "black"}
            }

            view_state = pdk.ViewState(
                latitude=df["latitude"].mean(),
                longitude=df["longitude"].mean(),
                zoom=11,
                pitch=0,
            )

            st.pydeck_chart(pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip=tooltip,
                map_style="mapbox://styles/mapbox/light-v9"  # ✅ Fond gris clair
            ))

            # ✅ Tableau sans index
            st.dataframe(
                df[["Nom de l'établissement", "Nom long de la formation", "Types de formation", "Commune", "Lien vers la fiche formation"]].dropna(),
                use_container_width=True,
                hide_index=True  # ⚡ Solution Streamlit 1.30+ pour cacher index
            )

            st.markdown("---")
            st.markdown("**Sources de données :** [Cartographie Formations Parcoursup - Ministère de l'Éducation](https://data.education.gouv.fr/explore/dataset/fr-esr-cartographie_formations_parcoursup/table/?disjunctive.tf&disjunctive.nm&disjunctive.fl&disjunctive.nmc&disjunctive.amg&sort=-annee)")



        with col1:
            show_formation_map(villes_gauche, commune_gauche)

        with col2:
            show_formation_map(villes_droite, commune_droite)
