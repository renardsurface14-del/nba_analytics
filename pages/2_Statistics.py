import pandas as pd
import streamlit as st
import plotly.express as px

# Lancer avec : py -m streamlit run test.py
st.set_page_config(layout="wide")

# -------------------------------
# Barre de navigation
# -------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.page_link("home.py",                   label=" Accueil")
with c2: st.page_link("pages/1_Team.py",           label=" Équipe")
with c3: st.page_link("pages/2_Statistics.py",     label=" Statistiques")
with c4: st.page_link("pages/3_Champ_Historic.py", label=" Historique")
with c5: st.page_link("pages/4_Trade_Machine.py",  label=" Simulateur de Trade")


# Charger les données
df_reg_season_players = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
df_playoff_players = pd.read_excel("data/df_playoff_players_filtered.xlsx")

# -------------------------------
# Titre principal
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>NBA 2024-25 Statistiques</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center; color: gray;'>Les chiffres derrière les performances</h3>", 
    unsafe_allow_html=True
)

# -------------------------------
# Filtres
# -------------------------------
col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="large")

with col1:
    metric_filter = st.selectbox(
        "Choisir une vue", 
        ["Leaders", "Top 30", "Toutes les données"],
        key="metric_filter"
    )

with col2:
    season_filter = st.radio(
        "Partie de la saison", 
        ["Saison régulière", "Playoffs"], 
        horizontal=True,
        key="season_filter"
    )
with col3:
    stat_mode = st.radio(
        "Mode statistique", 
        ["Par match", "Total"], 
        horizontal=True,
        key="stat_mode"
    )

# Affichage conditionnel du mode d'affichage
if metric_filter in ["Top 30", "Toutes les données"]:
    view_mode = "Tableau"  # forcé en tableau
else:
    with col4:
        view_mode = st.radio(
            "Mode d'affichage", 
            ["Tableau", "Diagramme en barres"], 
            horizontal=True,
            key="view_mode"
        )


# -------------------------------
# Sélection du dataset
# -------------------------------
df = df_reg_season_players if season_filter == "Saison régulière" else df_playoff_players
df = df[(df["GP"] > 10) & (df["MIN_PG"] > 10)]

# -------------------------------
# Utilitaire : graphique en barres
# -------------------------------
def graphique_barres(data, col_name, titre):
    
    # Renommer la colonne avant de trier
    data = data.rename(columns={"PLAYER_NAME": "PLAYER"})
    data_sorted = data.sort_values(by=col_name, ascending=False)

    fig = px.bar(
        data_sorted,
        x=col_name,
        y="PLAYER",
        orientation="h",
        color="TEAM",
        title=titre,
        text=col_name,
        category_orders={"PLAYER": data_sorted["PLAYER"].tolist()}
    )

    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        insidetextanchor="end",
        textfont=dict(color="grey", size=14, family="Arial")
    )

    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        bargap=0.2,
        plot_bgcolor="white",
        showlegend=True
    )

    return fig


# -------------------------------
# Fonctions d'affichage
# -------------------------------
def afficher_offensif(df, label, mode, view_mode):
    suffix = "_PG" if mode == "Par match" else ""
    st.markdown(f"##  Statistiques offensives ({label} - {mode})")

    stats = {
        "Points": "PTS",
        "Passes décisives": "AST",
        "3 points marqués": "FG3M",
        "Lancers francs marqués": "FTM"
    }

    col1, col2 = st.columns(2)
    for (titre, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        top_data = df[["PLAYER_NAME", "TEAM", col_name + suffix]].sort_values(by=col_name + suffix, ascending=False).head(5)
        if view_mode == "Tableau":
            col.markdown(f"### {titre} {mode}")
            col.dataframe(top_data, hide_index=True, use_container_width=True)
        else:
            fig = graphique_barres(top_data, col_name + suffix, f"{titre}")
            col.plotly_chart(fig, use_container_width=True)

def afficher_defensif(df, label, mode, view_mode):
    suffix = "_PG" if mode == "Par match" else ""
    st.markdown(f"##  Statistiques défensives ({label} - {mode})")

    stats = {
        "Rebonds totaux": "REB",
        "Rebonds défensifs": "DREB",
        "Contres": "BLK",
        "Interceptions": "STL"
    }

    col1, col2 = st.columns(2)
    for (titre, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        top_data = df[["PLAYER_NAME", "TEAM", col_name + suffix]].sort_values(by=col_name + suffix, ascending=False).head(5)
        if view_mode == "Tableau":
            col.markdown(f"### {titre} {mode}")
            col.dataframe(top_data, hide_index=True, use_container_width=True)
        else:
            fig = graphique_barres(top_data, col_name + suffix, f"{titre}")
            col.plotly_chart(fig, use_container_width=True)
            



# -------------------------------
# Fonction pour choisir les colonnes
# -------------------------------
def pick_display_columns(
    df: pd.DataFrame,
    base_cols=("TEAM", "PLAYER_NAME", "PTS_PG", "AST_PG", "REB_PG", "MIN_PG"),
    exclude=("PLAYER_ID", "NICKNAME", "TEAM_ABBREVIATION"),
    key="col_picker"
) -> list:
    """Sélecteur de colonnes avec exclusions et option 'Tout sélectionner'."""
    exclude = set(exclude)
    available = [c for c in df.columns if c not in exclude]
    defaults = [c for c in base_cols if c in available]
    extras = [c for c in available if c not in defaults]

    options = ["Tout sélectionner"] + extras
    selected_extra = st.multiselect(
        "Ajouter des colonnes à afficher",
        options=options,
        default=[],
        key=key
    )
    if "Tout sélectionner" in selected_extra:
        selected_extra = extras
    return defaults + selected_extra

# -------------------------------
# Affichage selon les filtres
# -------------------------------
if metric_filter == "Leaders":
    afficher_offensif(df, season_filter, stat_mode, view_mode)
    st.divider()
    afficher_defensif(df, season_filter, stat_mode, view_mode)

elif metric_filter == "Top 30":
    stat_choice = st.selectbox(
        "Sélectionner une statistique",
        [
            "Points",
            "Passes décisives",
            "Rebonds totaux",
            "Rebonds offensifs",
            "Rebonds défensifs",
            "Minutes",
            "3 points marqués",
            "Lancers francs marqués",
            "Contres",
            "Interceptions",
            "Ballons perdus",
        ]
    )
    suffix = "_PG" if stat_mode == "Par match" else ""
    stat_map = {
        "Points": "PTS",
        "Passes décisives": "AST",
        "Rebonds totaux": "REB",
        "Rebonds offensifs": "OREB",
        "Rebonds défensifs": "DREB",
        "Minutes": "MIN",
        "3 points marqués": "FG3M",
        "Lancers francs marqués": "FTM",
        "Contres": "BLK",
        "Interceptions": "STL",
        "Ballons perdus": "TOV",
    }

    chosen_col = stat_map[stat_choice] + suffix
    top30 = (
        df[["PLAYER_NAME", "TEAM", chosen_col]]
        .sort_values(by=chosen_col, ascending=False)
        .head(30)
    )

    st.markdown(f"##  Top 30 {stat_choice} ({stat_mode}) - {season_filter}")
    st.dataframe(top30, hide_index=True, use_container_width=True)

elif metric_filter == "Toutes les données":
    st.markdown(f"##  {season_filter} — Données complètes (par champ)")

    cols_to_show = pick_display_columns(
        df,
        base_cols=("TEAM", "PLAYER_NAME", "PTS_PG", "AST_PG", "REB_PG", "MIN_PG"),
        exclude=("PLAYER_ID", "NICKNAME", "TEAM_ABBREVIATION"),
        key="all_data_fields"
    )

    if cols_to_show:
        st.dataframe(df[cols_to_show], hide_index=True, use_container_width=True)
    else:
        st.info("Aucune colonne sélectionnée. Veuillez en choisir au moins une.")
