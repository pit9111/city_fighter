# City Fighter - Comparaison entre deux villes

## Présentation

L'objectif de ce projet est de comparer deux villes selon plusieurs critères (démographie, emploi, logement, météo, culture) en utilisant des données ouvertes (APIs publiques et bases de données nationales).  
L'application permet à l'utilisateur de sélectionner deux villes et d'obtenir des comparaisons interactives à l'aide de visualisations modernes.

Lien de l'application : https://cityfighter-7yxz6pvskz6kdkm8gctvkr.streamlit.app/
## Structure du projet
```sh
CITY/
├── app.py
├── data/
│   ├── communes_synthetique.csv
│   ├── communes-france-2025 (1).csv
│   ├── guide-utilisation-des-donnees.pdf
│   ├── pred-app-mef-dhup.csv
├── utils/
│   ├── clim.py
│   ├── climat.py
│   ├── csv_traitement.py
│   ├── loyer.py
│   ├── meteo.py
│   └── wiki.py


