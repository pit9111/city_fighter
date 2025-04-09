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
