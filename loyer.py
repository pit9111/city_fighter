import streamlit as st
import pandas as pd

# --- Chargement des fichiers CSV ---
@st.cache_data
def load_data():
    return pd.read_csv("communes_synthetique.csv")

@st.cache_data
def load_loyer_data():
    df_loyer = pd.read_csv("pred-app-mef-dhup.csv", encoding="latin1", sep=";")
    df_loyer.columns = df_loyer.columns.str.strip()
    df_loyer["INSEE_C"] = df_loyer["INSEE_C"].astype(str).str.strip()

    # 🆕 Conversion des colonnes numériques
    for col in ["loypredm2", "lwr.IPm2", "upr.IPm2"]:
        df_loyer[col] = df_loyer[col].astype(str).str.replace(",", ".")
        df_loyer[col] = pd.to_numeric(df_loyer[col], errors="coerce")

    return df_loyer


# --- Fonction pour récupérer les infos de loyer ---
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

# --- Interface Streamlit ---
st.set_page_config(page_title="Loyer par commune", layout="centered")

st.title("🏡 Consultation des Loyers par Commune")

# Chargement des données
df_communes = load_data()
df_loyer = load_loyer_data()

# Sélection d'une commune
communes = sorted(df_communes["nom_standard"].unique())
selected_commune = st.selectbox("Choisissez une commune", communes)

# Affichage des données si sélection
if selected_commune:
    row = df_communes[df_communes["nom_standard"] == selected_commune].iloc[0]
    code_insee = str(row["code_insee"])
    loyer_info = get_loyer_info(code_insee, df_loyer)
    st.subheader(f"📍 Données pour {selected_commune} (INSEE : {code_insee})")

    if loyer_info:
        st.success("Données trouvées pour la commune !")
        st.write(f"**Prix moyen au m²** : {loyer_info['loypredm2']} €/m²")
        st.write(f"**Intervalle estimé** : {loyer_info['lwr']} € - {loyer_info['upr']} € /m²")
        st.write(f"**Nombre d'annonces analysées** : {loyer_info['nbobs']}")
        if loyer_info['nbobs'] < 30:
            st.warning("⚠️ Attention : données peu fiables (moins de 30 observations)")
    else:
        st.error("Aucune donnée disponible pour cette commune.")
