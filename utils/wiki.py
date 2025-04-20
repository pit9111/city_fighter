import streamlit as st
import requests

st.set_page_config(page_title="Image de ville par code INSEE", page_icon="🏙️")

st.title("🏙️ Image de présentation d'une ville")
insee_code = st.text_input("Entre un code INSEE :", "35238")

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
        title = full_url.split("/wiki/")[-1]
        return title
    return None

@st.cache_data
def get_wikipedia_thumbnail(title):
    url = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{title}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("thumbnail", {}).get("source", None), data.get("title"), data.get("extract")
    return None, None, None

if insee_code:
    with st.spinner("🔎 Recherche en cours..."):
        title = get_wikipedia_title_from_insee(insee_code)
        if title:
            image_url, city_name, extract = get_wikipedia_thumbnail(title)
            if image_url:
                st.image(image_url, caption=f"{city_name}", use_container_width=True)
                if extract:
                    st.info(extract)
            else:
                st.warning("❌ Aucune image trouvée pour cette ville.")
        else:
            st.error("❌ Aucune page Wikipédia trouvée pour ce code INSEE.")
