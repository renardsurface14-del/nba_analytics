import unicodedata
import pandas as pd
import streamlit as st
import plotly.express as px

# --------------------------------------------------
# Lancer avec :  streamlit run 3_Champ_Historic.py
# --------------------------------------------------
st.set_page_config(page_title="Historique NBA", layout="wide")

# -------------------------------
# Barre de navigation (haut de page)
# -------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.page_link("home.py",                   label=" Accueil")
with c2:
    st.page_link("pages/1_Team.py",           label=" Équipe")
with c3:
    st.page_link("pages/2_Statistics.py",     label=" Statistiques")
with c4:
    st.page_link("pages/3_Champ_Historic.py", label=" Historique")
with c5:
    st.page_link("pages/4_Trade_Machine.py",  label=" Simulateur de Trade")

# -------------------------------
# Chargement des données
# -------------------------------
@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    # Normalisation minimale des noms de colonnes pour robustesse
    df.columns = [c.strip() for c in df.columns]
    # Unifier le nom de la colonne des finalistes (RUNNER) 
    df["RUNNER"] = df["RUNNER-UP"]
    return df


df_raw = load_data("data/df_nba_champion.xlsx")

#st.dataframe(df_raw)

st.markdown(
    """
    <h1 style='text-align:center;margin-top:0'>Historique NBA — depuis 1976</h1>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# Functions
# -------------------------------

def normalize_txt(s: str) -> str:
    """Minuscule + trim + suppression des accents. Gère None/NaN."""
    if s is None:
        return ""
    s = str(s)
    if s.lower() == "nan":
        return ""
    s = s.strip().casefold()
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return s


def graphique_barres(data: pd.DataFrame, col_valeur: str, col_label: str, titre: str, col_couleur: str | None = None):
    """Graphique en barres horizontales (top to bottom) avec valeurs affichées."""
    data_sorted = data.sort_values(by=col_valeur, ascending=False)  # ascending False pour barres du haut vers le bas

    kwargs = dict(
        data_frame=data_sorted,
        x=col_valeur,
        y=col_label,
        orientation="h",
        title=titre,
        text=col_valeur,
        category_orders={col_label: data_sorted[col_label].tolist()},
    )
    if col_couleur:
        kwargs["color"] = col_couleur

    fig = px.bar(**kwargs)

    fig.update_traces(
        texttemplate="%{text}",
        textposition="outside",
        insidetextanchor="end",
        textfont=dict(color="grey", size=14, family="Arial"),
        marker_line_width=0,
    )

    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        bargap=0.05,
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=120, r=40, t=60, b=40),
        title=dict(x=0.02, xanchor="left"),
    )
    return fig


# -------------------------------
# Préparation des colonnes normalisées
# -------------------------------
df = df_raw.copy()
for col in ["CHAMPION", "RUNNER", "FINALS_MVP", "POINTS", "REBOUNDS", "ASSISTS"]:
    df[f"{col}_NORM"] = df[col].map(normalize_txt)

# Colonne concaténée (pour le filtre joueur, recherche exacte et robuste)
df["PLAYERS_ALL_NORM"] = (
    df["FINALS_MVP_NORM"].fillna("") + "|" +
    df["POINTS_NORM"].fillna("") + "|" +
    df["REBOUNDS_NORM"].fillna("") + "|" +
    df["ASSISTS_NORM"].fillna("")
)

# -------------------------------
# Onglets
# -------------------------------
onglet_hist, onglet_stats = st.tabs([" Tableau d'honneur", " Bilan des franchises"])  # guillemets simples dans le label

# ===== Onglet 1 : Historique des champions =====
with onglet_hist:
    st.markdown("### Filtrer le palmarès")

    # Listes d'options (indépendantes, depuis le DF complet)
    years = ["Toutes"] + sorted([y for y in df["YEAR"].dropna().unique().tolist()], reverse=True)
    champs = ["Toutes"] + sorted([c for c in df["CHAMPION"].dropna().unique().tolist()])
    runners = ["Toutes"] + sorted([r for r in df["RUNNER"].dropna().unique().tolist()])
    players = ["Toutes"] + sorted(
        pd.concat([
            df["FINALS_MVP"].dropna(),
            df["POINTS"].dropna(),
            df["REBOUNDS"].dropna(),
            df["ASSISTS"].dropna(),
        ]).astype(str).unique().tolist()
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        year_filter = st.selectbox("Sélectionner une année", years, key="year_hist")
    with col2:
        champ_filter = st.selectbox("Sélectionner une équipe championne", champs, key="champ_hist")
    with col3:
        runner_filter = st.selectbox("Sélectionner une équipe finaliste", runners, key="runner_hist")
    with col4:
        player_filter = st.selectbox("Sélectionner un joueur", players, key="player_hist")

    # Application cumulative des filtres (AND)
    filtered = df.copy()

    def apply_eq(_df: pd.DataFrame, col: str, val):
        return _df if val == "Toutes" else _df[_df[col] == val]

    filtered = apply_eq(filtered, "YEAR", year_filter)
    filtered = apply_eq(filtered, "CHAMPION", champ_filter)
    filtered = apply_eq(filtered, "RUNNER", runner_filter)

    if player_filter != "Toutes":
        player_norm = normalize_txt(player_filter)
        # Recherche exacte sur l'une des 4 colonnes (via split de la concat)
        filtered = filtered[filtered["PLAYERS_ALL_NORM"].str.split("|").apply(lambda lst: player_norm in lst)]

    st.markdown("### Résultats")

    # Colonnes techniques à masquer
    tech_cols = [c for c in filtered.columns if c.endswith("_NORM") or c == "PLAYERS_ALL_NORM"]

    if filtered.empty:
        st.info("Aucun résultat pour cette combinaison de filtres.")
    else:
        st.dataframe(
            filtered.drop(columns=tech_cols, errors="ignore"),
            hide_index=True,
            use_container_width=True,
        )

# ===== Onglet 2 : Statistiques globales d’équipe =====
with onglet_stats:
    st.markdown("### Vue d’ensemble — franchises")

    # 1) Plus de titres par équipe (Top 10)
    titles_count = (
        df.groupby("CHAMPION").size().reset_index(name="Titres").sort_values(by="Titres", ascending=False).head(10)
    )

    # 2) Plus de trophées Finals MVP par joueur (Top 10)
    mvp_count = (
        df[df["FINALS_MVP"].notna()]
        .groupby("FINALS_MVP").size().reset_index(name="Trophées MVP")
        .sort_values(by="Trophées MVP", ascending=False).head(10)
    )

    # 3) Plus de participations en finales par équipe (Top 10)
    team_appearances = (
        pd.concat([
            df[["CHAMPION"]].rename(columns={"CHAMPION": "Équipe"}),
            df[["RUNNER"]].rename(columns={"RUNNER": "Équipe"}),
        ])
        .dropna()
        .groupby("Équipe").size().reset_index(name="Participations")
        .sort_values(by="Participations", ascending=False).head(10)
    )

    # Affichages + graphiques
    left, mid, right = st.columns(3)

    with left:
        #st.markdown("#### Top 10 équipes par nombre de titres")
        #st.dataframe(titles_count, hide_index=True, use_container_width=True)
        fig1 = graphique_barres(titles_count, col_valeur="Titres", col_label="CHAMPION", titre="Titres par équipe")
        st.plotly_chart(fig1, use_container_width=True, theme="streamlit")

    with mid:
        #st.markdown("#### Top 10 joueurs avec le plus de Finals MVP")
        #st.dataframe(mvp_count, hide_index=True, use_container_width=True)
        fig2 = graphique_barres(mvp_count, col_valeur="Trophées MVP", col_label="FINALS_MVP", titre="Finals MVP — cumul")
        st.plotly_chart(fig2, use_container_width=True, theme="streamlit")

    with right:
        #st.markdown("#### Top 10 équipes par participations en finales")
        #st.dataframe(team_appearances, hide_index=True, use_container_width=True)
        fig3 = graphique_barres(team_appearances, col_valeur="Participations", col_label="Équipe", titre="Participations en finales")
        st.plotly_chart(fig3, use_container_width=True, theme="streamlit")
