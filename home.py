# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd

# -------------------------------
# Configuration de la Page
# -------------------------------
st.set_page_config(page_title="Tableau de Bord NBA", layout="wide") # Configure le titre de la page et la disposition large

# -------------------------------
# Affichage de la Barre de Navigation
# -------------------------------

# Note : La barre de navigation est actuellement implémentée directement via st.page_link
c1, c2, c3, c4,c5= st.columns(5) # Crée 5 colonnes pour les liens de navigation
with c1: st.page_link("home.py",                   label=" Accueil") # Lien vers la page d'accueil
with c2: st.page_link("pages/1_Team.py",           label=" Équipe") # Lien vers la page d'équipe
with c3: st.page_link("pages/2_Statistics.py",     label=" Statistiques") # Lien vers la page de statistiques
with c4: st.page_link("pages/3_Champ_Historic.py", label=" Historique") # Lien vers la page historique des champions
with c5: st.page_link("pages/4_Trade_Machine.py",  label=" Machine à Trade") # Lien vers la machine à trade


# -------------------------------
# Chargement des Données (cache) => But : éviter de relire 5 Excel à chaque interaction.
# -------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def load_data():
    df_west  = pd.read_excel("data/df_western_conf_standing.xlsx")
    df_east  = pd.read_excel("data/df_eastern_conf_standing.xlsx")
    df_team_ratings = pd.read_excel("data/df_nba_team_reg_season_ratings.xlsx")
    df_players = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
    df_salaries = pd.read_excel("data/df_nba_players_salaries.xlsx")
    return df_west, df_east, df_team_ratings, df_players, df_salaries

with st.spinner("Chargement des données..."):
    df_west, df_east, df_team_ratings, df_players, df_salaries = load_data()

# ton filtrage existant
df_players = df_players[(df_players["GP"] > 10) & (df_players["MIN_PG"] > 10)]

# -------------------------------
# Titre de la Page
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'> Aperçu NBA 2024-25</h1>",
    unsafe_allow_html=True # Permet le rendu HTML
)
st.markdown(
    "<h4 style='text-align: center; color: gray;'>Un Regard Global sur la Ligue</h4>",
    unsafe_allow_html=True # Permet le rendu HTML
)


# -------------------------------
# Onglets de Navigation
# -------------------------------
# Crée des onglets pour organiser le contenu de la page
tab1, tab2, tab3, tab4 = st.tabs([
    " Classements des Conférences",
    " Meilleurs Joueurs",
    " Évaluations des Équipes",
    " Salaires"
])

# -------------------------------
# Contenu de l'Onglet 1 : Classements des Conférences
# -------------------------------
with tab1:
    st.markdown("##  Classements des Conférences") # Titre de l'onglet

    col1, col2 = st.columns(2) # Crée deux colonnes pour afficher les conférences côte à côte
    with col1:
        st.markdown("### Conférence Ouest") # Sous-titre pour la Conférence Ouest
        st.dataframe(df_west, hide_index=True, use_container_width=True) # Affiche le DataFrame de la Conférence Ouest
    with col2:
        st.markdown("### Conférence Est") # Sous-titre pour la Conférence Est
        st.dataframe(df_east, hide_index=True, use_container_width=True) # Affiche le DataFrame de la Conférence Est

# -------------------------------
# Contenu de l'Onglet 2 : Meilleurs Joueurs
# -------------------------------
with tab2:
    st.markdown("##  Top 3 des Joueurs par Métriques Clés") # Titre de l'onglet

    # Filtre de sélection d'équipe unique avec l'option "Toutes les équipes"
    all_teams = sorted(df_players["TEAM"].dropna().unique()) # Récupère la liste unique des équipes
    team_choice = st.selectbox(
        "Équipe",
        options=["Toutes les équipes"] + all_teams, # Ajoute "Toutes les équipes" comme première option
        index=0, # Sélectionne la première option par défaut
        key="top_players_team_filter_single" # Clé unique pour le widget
    )

    # Applique le filtre localement
    df_tp = df_players.copy() # Crée une copie du DataFrame des joueurs
    if team_choice != "Toutes les équipes": # Si une équipe spécifique est choisie
        df_tp = df_tp[df_tp["TEAM"] == team_choice] # Filtre le DataFrame par l'équipe sélectionnée

    metrics = {
        "Points Par Match": "PTS_PG",
        "Rebonds Par Match": "REB_PG",
        "Passes Décisives Par Match": "AST_PG"
    } # Dictionnaire des métriques à afficher

    # Itère sur chaque métrique pour afficher les 3 meilleurs joueurs
    for label, col_name in metrics.items():

        top3 = (
            df_tp[["PLAYER_NAME", "TEAM", col_name]] # Sélectionne les colonnes Joueur, Équipe et la métrique
            .sort_values(by=col_name, ascending=False) # Trie par la métrique en ordre décroissant
            .head(3) # Prend les 3 premiers joueurs
        )
        st.markdown(f"### {label}") # Affiche le titre de la métrique
        st.dataframe(top3, hide_index=True, use_container_width=True) # Affiche le DataFrame des 3 meilleurs

# -------------------------------
# Contenu de l'Onglet 3 : Évaluations des Équipes
# -------------------------------
with tab3:
    st.markdown("##  Évaluations de Performance des Équipes (Top 10)") # Titre de l'onglet

    col1, col2, col3 = st.columns(3) # Crée trois colonnes pour les différentes évaluations

    # Offensive Rating (plus élevé est mieux)
    with col1:
        st.markdown("### Évaluation Offensive") # Sous-titre
        off = df_team_ratings[["TEAM", "ORTG"]].sort_values(by="ORTG", ascending=False).head(10) # Trie et prend les 10 meilleures
        st.dataframe(off, hide_index=True, use_container_width=True) # Affiche le DataFrame
       

    # Defensive Rating (plus faible est mieux → ordre croissant)
    with col2:
        st.markdown("### Évaluation Défensive") # Sous-titre
        deff = df_team_ratings[["TEAM", "DRTG"]].sort_values(by="DRTG", ascending=True).head(10) # Trie et prend les 10 meilleures
        st.dataframe(deff, hide_index=True, use_container_width=True) # Affiche le DataFrame
        

    # Net Rating (plus élevé est mieux)
    with col3:
        st.markdown("### Évaluation Nette") # Sous-titre
        net = df_team_ratings[["TEAM", "NRTG"]].sort_values(by="NRTG", ascending=False).head(10) # Trie et prend les 10 meilleures
        st.dataframe(net, hide_index=True, use_container_width=True) # Affiche le DataFrame

# -------------------------------
# Contenu de l'Onglet 4 : Salaires (team -> joueurs)
# -------------------------------
with tab4:
    st.markdown("## Salaires")

    TEAM_ALL, PLAYER_ALL = "Toutes les équipes", "Tous les joueurs"

    # 1) Sélecteur Équipe
    team_options = [TEAM_ALL] + sorted(df_salaries["TEAM"].dropna().unique())
    team_sel = st.selectbox("Équipe", team_options, index=0, key="sal_team")

    # 2) Liste des joueurs dépendante de l'équipe
    if team_sel == TEAM_ALL:
        player_options = [PLAYER_ALL] + sorted(df_salaries["PLAYER"].dropna().unique())
    else:
        player_options = [PLAYER_ALL] + sorted(
            df_salaries.loc[df_salaries["TEAM"] == team_sel, "PLAYER"].dropna().unique()
        )

    # Conserver la sélection joueur si encore valide, sinon reset sur "Tous"
    prev_player = st.session_state.get("sal_player", PLAYER_ALL)
    player_index = player_options.index(prev_player) if prev_player in player_options else 0
    player_sel = st.selectbox("Joueur", player_options, index=player_index, key="sal_player")

    # 3) Filtrage (sans jamais modifier l’équipe via le joueur)
    df_filtered = df_salaries
    if team_sel != TEAM_ALL:
        df_filtered = df_filtered[df_filtered["TEAM"] == team_sel]
    if player_sel != PLAYER_ALL:
        df_filtered = df_filtered[df_filtered["PLAYER"] == player_sel]

    # 4) Affichage
    if df_filtered.empty:
        st.info("Aucun résultat pour ces filtres.")
    else:
        st.dataframe(df_filtered, hide_index=True, use_container_width=True)
