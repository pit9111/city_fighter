import pandas as pd

# Chargement du fichier CSV
df = pd.read_csv("data/communes-france-2025 (1).csv")

# Colonnes à conserver
colonnes_a_garder = [
    "code_insee", "nom_standard", "dep_nom", "reg_nom",
    "population", "superficie_km2", "grille_densite_texte",
    "code_postal", "url_wikipedia", "latitude_centre", "longitude_centre"
]

# Filtrage des colonnes
df_filtre = df[colonnes_a_garder]

# Filtrage sur la population
df_filtre = df_filtre[df_filtre["population"] > 20000]

# Ajout des coordonnées manquantes pour certaines grandes villes
coordonnees = {
    "Paris": {"latitude_centre": 48.8566, "longitude_centre": 2.3522},
    "Lyon": {"latitude_centre": 45.7640, "longitude_centre": 4.8357},
    "Marseille": {"latitude_centre": 43.2965, "longitude_centre": 5.3698}
}

for ville, coords in coordonnees.items():
    mask = df_filtre["nom_standard"].str.lower() == ville.lower()
    if mask.any():
        df_filtre.loc[mask, "latitude_centre"] = coords["latitude_centre"]
        df_filtre.loc[mask, "longitude_centre"] = coords["longitude_centre"]
        print(f"Coordonnées ajoutées pour {ville}")
    else:
        print(f"{ville} non trouvé dans le fichier filtré.")

# Sauvegarde du nouveau CSV
df_filtre.to_csv("data/communes_synthetique.csv", index=False)
