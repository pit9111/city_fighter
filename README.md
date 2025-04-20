# City Fighter - Comparaison entre deux villes

## Project Objectives

L'objectif de ce projet est de comparer deux villes selon plusieurs critères (démographie, emploi, logement, météo, culture) en utilisant des données ouvertes (APIs publiques et bases de données nationales).  
L'application permet à l'utilisateur de sélectionner deux villes et d'obtenir des comparaisons interactives à l'aide de visualisations modernes.

Lien de l'application : 
## Project Structure
```sh
CITY_FIGHTER/
├── .github/
│   └── workflows/
│       ├── ci.yml  # GitHub Actions pour CI/CD
├── data/
│   ├── cities_insee.csv  # Données de base sur les villes (INSEE)
│   └── additional_data/  # Autres fichiers de données locales si nécessaire
├── src/
│   ├── __init__.py
│   ├── api_clients/
│   │   ├── insee_client.py  # Récupération des données INSEE
│   │   ├── meteo_client.py  # Récupération des données météo
│   │   └── wikipedia_client.py  # Récupération des infos culturelles
│   ├── data_processing/
│   │   ├── data_cleaning.py
│   │   └── data_merging.py
│   ├── visualizations/
│   │   ├── plots.py
│   ├── app.py  # Application principale Streamlit
├── tests/
│   ├── test_api_clients.py
│   ├── test_data_processing.py
│   ├── test_visualizations.py
├── .gitignore
├── README.md
├── requirements.txt
├── city_fighter_demo.ipynb  # Notebook Jupyter pour analyse exploratoire
