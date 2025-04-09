import pandas as pd

# Chargement du fichier CSV
df = pd.read_csv("communes-france-2025 (1).csv")

# Colonnes à conserver
colonnes_a_garder = [
    "code_insee", "nom_standard", "dep_nom", "reg_nom",
    "population", "superficie_km2", "grille_densite_texte",
    "code_postal", "url_wikipedia"
]

# Filtrage des colonnes
df_filtre = df[colonnes_a_garder]

# Filtrage sur la population
df_filtre = df_filtre[df_filtre["population"] > 20000]

# Sauvegarde du nouveau CSV
df_filtre.to_csv("communes_synthetique.csv", index=False)
