# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Configuration de la Page
# -------------------------------
st.set_page_config(page_title="Équipe", layout="wide")

# -------------------------------
# Barre de navigation (liens simples)
# -------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1: st.page_link("home.py",                   label=" Accueil")
with c2: st.page_link("pages/1_Team.py",           label=" Équipe")
with c3: st.page_link("pages/2_Statistics.py",     label=" Statistiques")
with c4: st.page_link("pages/3_Champ_Historic.py", label=" Historique")
with c5: st.page_link("pages/4_Trade_Machine.py",  label=" Machine à Trade")

# =========================================================
# CACHES
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_team_page_data():
    df_west         = pd.read_excel("data/df_western_conf_standing.xlsx")
    df_east         = pd.read_excel("data/df_eastern_conf_standing.xlsx")
    df_team_ratings = pd.read_excel("data/df_nba_team_reg_season_ratings.xlsx")
    df_reg_players  = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
    df_po_players   = pd.read_excel("data/df_playoff_players_filtered.xlsx")
    df_salaries     = pd.read_excel("data/df_nba_players_salaries.xlsx")
    return df_west, df_east, df_team_ratings, df_reg_players, df_po_players, df_salaries

@st.cache_data(ttl=3600, show_spinner=False)
def build_salaries_long_join(df_salaries: pd.DataFrame, df_reg_players: pd.DataFrame):
    # Colonnes d'années dynamiques (exclut PLAYER/TEAM/GUARANTEED)
    year_cols = [c for c in df_salaries.columns if c not in ["PLAYER", "TEAM"] and str(c).upper() != "GUARANTEED"]

    df_salaries_long = df_salaries.melt(
        id_vars=["PLAYER", "TEAM"],
        value_vars=year_cols,
        var_name="YEAR",
        value_name="SALARY"
    )

    # Jointure pour récupérer position et stats clés (depuis REG saison)
    df_players_slim = df_reg_players[["PLAYER_NAME", "TEAM", "POSITION", "PTS_PG", "AST_PG", "REB_PG"]].rename(
        columns={"PLAYER_NAME": "PLAYER"}
    )

    df_join = pd.merge(
        df_salaries_long,
        df_players_slim,
        how="left",
        on=["PLAYER", "TEAM"]
    )

    # SALARY_NUM numérique
    df_join["SALARY_NUM"] = (
        df_join["SALARY"]
        .astype(str)
        .str.replace(r"[^0-9]", "", regex=True)
        .replace("", "0")
        .astype(int)
    )
    return df_salaries_long, df_join

# =========================================================
# UTILITAIRES UI
# =========================================================
def render_kpi(df: pd.DataFrame, value_col: str, title: str):
    """Affiche une carte KPI pour le joueur ayant la valeur max de value_col."""
    if df.empty or value_col not in df.columns or df[value_col].dropna().empty:
        st.info(f"Aucune donnée pour {title}.")
        return

    idx = df[value_col].idxmax()
    row = df.loc[idx]
    val = float(row[value_col])
    player_name = str(row.get("PLAYER_NAME", "Inconnu"))

    width_px = 320
    st.markdown(
        f"""
        <div style="background:#17408B; color:#FFFFFF; padding:16px; border-radius:12px; width:{width_px}px;">
            <div style="font-size:14px; opacity:.85; margin-bottom:6px; text-align:center;">{title}</div>
            <div style="font-size:32px; font-weight:700; line-height:1; text-align:center;">{val:.1f}</div>
            <div style="font-size:13px; opacity:.9; margin-top:6px; text-align:center;">{player_name}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_kpi_box(title: str, value_text: str, subtitle: str = ""):
    """Carte KPI générique."""
    width_px = 320
    st.markdown(
        f"""
        <div style="background:#17408B; color:#FFFFFF; padding:16px; border-radius:12px; width:{width_px}px;">
            <div style="font-size:14px; opacity:.85; margin-bottom:6px; text-align:center;">{title}</div>
            <div style="font-size:32px; font-weight:700; line-height:1; text-align:center;">{value_text}</div>
            <div style="font-size:13px; opacity:.9; margin-top:6px; text-align:center;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

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

# =========================================================
# CHARGEMENT DES DONNÉES
# =========================================================
df_west, df_east, df_team_ratings, df_reg_players, df_po_players, df_salaries = load_team_page_data()

# Filtre qualité (cohérent avec ta home) : GP>10 & MIN_PG>10
df_reg_players = df_reg_players[(df_reg_players["GP"] > 10) & (df_reg_players["MIN_PG"] > 10)]
df_po_players  = df_po_players[(df_po_players["GP"] >= 4) & (df_po_players["MIN_PG"] > 10)]

# Build salaires long + join (caché)
df_salaries_unpivoted, df_join = build_salaries_long_join(df_salaries, df_reg_players)

# =========================================================
# TITRE
# =========================================================
st.markdown("<h1 style='text-align: center;'> Aperçu de l'Équipe NBA 2024-25</h1>", unsafe_allow_html=True)

# =========================================================
# FILTRE GLOBAL ÉQUIPE
# =========================================================
team_options = sorted(df_reg_players["TEAM"].dropna().unique())
selected_team = st.selectbox("Sélectionnez une Équipe", team_options, index=0, key="team_filter")

# =========================================================
# STANDINGS (conf + rang)
# =========================================================
df_west_local = df_west.copy()
df_east_local = df_east.copy()
df_west_local["CONF"] = "Ouest"
df_east_local["CONF"] = "Est"
df_west_local["RANK"] = range(1, len(df_west_local) + 1)
df_east_local["RANK"] = range(1, len(df_east_local) + 1)
df_standings = pd.concat([df_east_local, df_west_local], ignore_index=True)

def to_bool_playoff(x):
    s = str(x).strip().lower()
    return s in ("*", "true", "1")

if "PLAYOFF_TEAM" in df_standings.columns:
    if df_standings["PLAYOFF_TEAM"].dtype != bool:
        df_standings["PLAYOFF_TEAM"] = df_standings["PLAYOFF_TEAM"].apply(to_bool_playoff)
else:
    df_standings["PLAYOFF_TEAM"] = False

team_row = df_standings[df_standings["TEAM"] == selected_team]
if not team_row.empty:
    conf = team_row.iloc[0]["CONF"]
    rank = int(team_row.iloc[0]["RANK"])
    st.markdown(f"**Conférence :** {conf} — **Rang :** #{rank}")
else:
    st.info("Équipe sélectionnée non trouvée dans les classements.")

# =========================================================
# SAISON (REG vs PO) + DATAFRAME COURANT
# =========================================================
season_filter = st.radio(
    "Filtrez les Statistiques selon la partie de la saison",
    ["Saison Régulière", "Playoffs"],
    horizontal=True,
    key="season_filter_team"
)

df_current = df_reg_players if season_filter == "Saison Régulière" else df_po_players
df_current = df_current[df_current["TEAM"] == selected_team]

if season_filter == "Playoffs":
    row = df_standings[df_standings["TEAM"] == selected_team]
    is_po = bool(row["PLAYOFF_TEAM"].iloc[0]) if not row.empty else False
    if not is_po:
        st.warning(f"{selected_team} n'a pas participé aux playoffs en 2024-25 — aucune statistique de joueur de playoffs à afficher.")
        st.stop()

st.markdown(f"### Statistiques de l'Équipe — {selected_team}")
st.markdown("## Statistiques Générales")

# =========================================================
# ONGLETS
# =========================================================
tab_stats, tab_salaries = st.tabs([" Statistiques de l'Équipe", " Salaires"])

# ===============================
# I. STATISTIQUES DE L'ÉQUIPE
# ===============================
with tab_stats:
    # KPIs 1
    c1, c2, c3 = st.columns(3)
    with c1: render_kpi(df_current, "PTS_PG", "Points par Match")
    with c2: render_kpi(df_current, "REB_PG", "Rebonds par Match")
    with c3: render_kpi(df_current, "AST_PG", "Passes Décisives par Match")

    st.markdown("<br>", unsafe_allow_html=True)

    # KPIs 2
    c4, c5, c6 = st.columns(3)
    with c4: render_kpi(df_current, "STL_PG", "Interceptions par Match")
    with c5: render_kpi(df_current, "BLK_PG", "Contres par Match")
    with c6: render_kpi(df_current, "TOV_PG", "Pertes de Balle par Match")

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # Effectif complet (avec exclusions centralisées)
    st.markdown("## Effectif Complet")
    cols_to_show = pick_display_columns(
        df_current,
        base_cols=("TEAM", "PLAYER_NAME", "PTS_PG", "AST_PG", "REB_PG", "MIN_PG"),
        exclude=("PLAYER_ID", "NICKNAME", "TEAM_ABBREVIATION"),
        key="team_full_fields"
    )
    if cols_to_show:
        st.dataframe(df_current[cols_to_show], hide_index=True, use_container_width=True)
    else:
        st.info("Aucune colonne sélectionnée. Veuillez en choisir au moins une.")

# ===============================
# II. SALAIRES
# ===============================
with tab_salaries:
    st.markdown(f"### Salaires des Joueurs — {selected_team}")

    # Liste d'années disponibles (hors 'GUARANTEED' déjà exclu en amont)
    all_years = sorted(df_salaries_unpivoted["YEAR"].dropna().unique())
    selected_year = st.selectbox("Sélectionnez la Saison", all_years, index=0, key="salary_year")

    df_team_year = df_join[(df_join["TEAM"] == selected_team) & (df_join["YEAR"] == selected_year)].copy()

    # KPIs salaires
    team_total = int(df_team_year["SALARY_NUM"].sum()) if not df_team_year.empty else 0
    if not df_team_year.empty and df_team_year["SALARY_NUM"].max() > 0:
        top_row = df_team_year.loc[df_team_year["SALARY_NUM"].idxmax()]
        top_player = str(top_row["PLAYER"])
        top_salary = int(top_row["SALARY_NUM"])
    else:
        top_player, top_salary = "—", 0

    df_val = df_team_year.copy()
    for c in ["PTS_PG", "AST_PG", "REB_PG"]:
        if c not in df_val.columns:
            df_val[c] = 0
    df_val[["PTS_PG", "AST_PG", "REB_PG"]] = df_val[["PTS_PG", "AST_PG", "REB_PG"]].fillna(0)
    df_val["salary_m"] = df_val["SALARY_NUM"].replace(0, pd.NA) / 1_000_000
    df_val["value_score"] = (df_val["PTS_PG"] + df_val["AST_PG"] + df_val["REB_PG"]) / df_val["salary_m"]

    if df_val["value_score"].dropna().empty:
        best_value_player, best_value_score = "—", 0.0
    else:
        best_row = df_val.loc[df_val["value_score"].idxmax()]
        best_value_player = str(best_row["PLAYER"])
        best_value_score = float(best_row["value_score"])

    c1, c2, c3 = st.columns(3)
    with c1: render_kpi_box("Masse Salariale de l'Équipe", f"${team_total:,.0f}", f"{selected_team} — {selected_year}")
    with c2: render_kpi_box("Joueur le Mieux Payé", f"${top_salary:,.0f}", top_player)
    with c3: render_kpi_box("Meilleure valeur (PTS+AST+REB / 1 M$)", f"{best_value_score:.1f}", best_value_player)
    
    # Pie salaires par position
    df_team_year = df_team_year[df_team_year["POSITION"].notna()]  # <-- exclut les joueurs sans position
    df_pie = (
        df_team_year.groupby("POSITION", as_index=False)["SALARY_NUM"]
        .sum()
        .sort_values("SALARY_NUM", ascending=False)
    )


    if df_pie.empty or df_pie["SALARY_NUM"].sum() == 0:
        st.info("Aucune donnée de salaire disponible pour cette équipe/année.")
    else:
        fig = px.pie(
            df_pie,
            names="POSITION",
            values="SALARY_NUM",
            title=f"Total des Salaires par Position — {selected_team} ({selected_year})",
            hole=0.35,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig.update_traces(
            textposition="inside",
            texttemplate="%{label}<br>$%{value:,.0f} (%{percent:.1%})",
            hovertemplate="%{label}<br>Total: $%{value:,.0f}<br>%{percent}",
            sort=False
        )
        fig.update_layout(margin=dict(t=60, b=30, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Afficher les lignes de joueurs pour cette saison"):
            # Tableau formaté ($)
            try:
                money_col = st.column_config.NumberColumn(format="$%,.0f")
                st.dataframe(
                    df_team_year[["PLAYER", "POSITION", "SALARY_NUM"]].rename(columns={"SALARY_NUM": "SALARY($)"}),
                    column_config={"SALARY($)": money_col},
                    hide_index=True,
                    use_container_width=True
                )
            except Exception:
                # fallback si la version de Streamlit ne supporte pas column_config
                st.dataframe(
                    df_team_year[["PLAYER", "POSITION", "SALARY_NUM"]].rename(columns={"SALARY_NUM": "SALARY($)"}),
                    hide_index=True,
                    use_container_width=True
                )
