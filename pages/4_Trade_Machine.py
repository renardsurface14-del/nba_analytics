# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px


# -------------------------------
# Afficher la barre de navigation
# -------------------------------
# --- Barre de navigation supérieure (officielle) ---
c1, c2, c3, c4,c5 = st.columns(5)
with c1: st.page_link("home.py",                   label=" Accueil")
with c2: st.page_link("pages/1_Team.py",           label=" Équipe")
with c3: st.page_link("pages/2_Statistics.py",     label=" Statistiques")
with c4: st.page_link("pages/3_Champ_Historic.py", label=" Historique")
with c5: st.page_link("pages/4_Trade_Machine.py",  label=" Machine à Échanges")


# -------------------------------
# Configuration de la page
# -------------------------------
st.set_page_config(page_title="Machine à Échanges de Joueurs", layout="wide")

st.title(" Machine à Échanges NBA")

st.write("Sélectionnez deux équipes et des joueurs pour simuler un échange. Les salaires seront comparés.")



# =========================================================
# CACHES
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def load_trade_machine_data():
    df_ouest        = pd.read_excel("data/df_western_conf_standing.xlsx")
    df_est          = pd.read_excel("data/df_eastern_conf_standing.xlsx")
    df_classements  = pd.read_excel("data/df_nba_team_reg_season_ratings.xlsx")
    df_joueurs_reg  = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
    df_joueurs_po   = pd.read_excel("data/df_playoff_players_filtered.xlsx")
    df_salaires     = pd.read_excel("data/df_nba_players_salaries.xlsx")
    return df_ouest, df_est, df_classements, df_joueurs_reg, df_joueurs_po, df_salaires

# Utilisation
df_ouest, df_est, df_classements_equipe, df_joueurs_reg, df_joueurs_po, df_salaires = load_trade_machine_data()


# -------------------------------
# Fonctions
# -------------------------------
def salaire_cumule(pool_df: pd.DataFrame, saison: str, joueurs_selectionnes: list[str]) -> int:
    """Retourne le salaire cumulé (déjà numérique) pour les joueurs sélectionnés."""
    if not joueurs_selectionnes or pool_df is None or saison not in pool_df.columns:
        return 0
    return int(pool_df.loc[pool_df["PLAYER"].isin(joueurs_selectionnes), saison].sum())

def formater_argent(montant: int) -> str:
    return f"${montant:,.0f}"

# Étape 1: Compter combien d'années de contrat valides chaque joueur a
annees_cols = ["2025-26","2026-27","2027-28","2028-29","2029-30","2030-31"]

# Remplacer les espaces réservés comme "None", "-", "" par NaN
df_salaires[annees_cols] = df_salaires[annees_cols].replace(
    ["None", "", "-", "—"], pd.NA
)

# Créer une nouvelle colonne avec le nombre d'années de contrat non nulles
df_salaires["contract_years"] = df_salaires[annees_cols].notna().sum(axis=1)

# Étape 2: Créer un sous-ensemble propre de df_joueurs_reg avec seulement les colonnes pertinentes
# Renommer PLAYER_NAME -> PLAYER pour s'aligner avec df_salaires
stat_cols = ["POSITION","AST_PG","BLK_PG","AGE","FG_PCT","FG3_PCT",
             "GP","MIN","PLUS_MINUS","PTS_PG","REB_PG","STL_PG","TOV_PG"]

df_reg_subset = (
    df_joueurs_reg
      .rename(columns={"PLAYER_NAME": "PLAYER"})
      [["PLAYER","TEAM"] + stat_cols]
)

# Étape 3: Fusionner les salaires et les statistiques des joueurs dans un seul dataframe
df_jointures = df_salaires.merge(df_reg_subset, on=["PLAYER","TEAM"], how="left")

# Prétraiter les colonnes de salaire: ne garder que les chiffres, convertir en int
for col in annees_cols + ["GUARANTEED"]:
    if col in df_jointures.columns:
        df_jointures[col] = (
            df_jointures[col]
            .astype(str)
            .str.replace(r"[^0-9]", "", regex=True)
            .replace("", "0")
            .astype(int)
        )

# -------------------------------
# Ligne 1: sélecteur de saison
# -------------------------------
SAISONS = ["2025-26","2026-27","2027-28","2028-29","2029-30","2030-31"]
saison = st.selectbox("Sélectionner la saison", SAISONS)

# -------------------------------
# Ligne 2: sélection d'équipe + joueur avec aperçu de l'effectif
# -------------------------------
colA, colB = st.columns(2)

liste_equipes = sorted(df_jointures["TEAM"].dropna().unique())

with colA:
    st.subheader("Équipe A")
    equipeA = st.selectbox("Choisir l'Équipe A", [""] + liste_equipes, key="equipeA")
    joueursA = []
    if equipeA == "":
        st.write("Veuillez sélectionner une équipe.")
    else:
        poolA = df_jointures[df_jointures["TEAM"] == equipeA].copy()

        # Afficher: JOUEUR, années_contrat, Salaire (saison sélectionnée), GUARANTEED
        affichageA = poolA[["PLAYER", "contract_years", saison, "GUARANTEED"]].copy()
        affichageA = affichageA.rename(columns={saison: "Salaire"})
        affichageA["Salaire"] = affichageA["Salaire"].map(formater_argent)
        affichageA["GUARANTEED"] = affichageA["GUARANTEED"].map(formater_argent)
        st.dataframe(affichageA, hide_index=True, use_container_width=True)

        # Sélection des joueurs (noms seulement; les détails sont affichés dans le tableau)
        joueursA = st.multiselect("Sélectionner les joueurs de l'Équipe A", poolA["PLAYER"].tolist(), key="joueursA")

with colB:
    st.subheader("Équipe B")
    # Supprimer l'Équipe A des options si sélectionnée
    options_equipe_B = [""] + [t for t in liste_equipes if t != equipeA]
    equipeB = st.selectbox("Choisir l'Équipe B", options_equipe_B, key="equipeB")
    joueursB = []
    if equipeB == "":
        st.write("Veuillez sélectionner une équipe.")
    else:
        poolB = df_jointures[df_jointures["TEAM"] == equipeB].copy()

        affichageB = poolB[["PLAYER", "contract_years", saison, "GUARANTEED"]].copy()
        affichageB = affichageB.rename(columns={saison: "Salaire"})
        affichageB["Salaire"] = affichageB["Salaire"].map(formater_argent)
        affichageB["GUARANTEED"] = affichageB["GUARANTEED"].map(formater_argent)
        st.dataframe(affichageB, hide_index=True, use_container_width=True)

        joueursB = st.multiselect("Sélectionner les joueurs de l'Équipe B", poolB["PLAYER"].tolist(), key="joueursB")


# -------------------------------
# Ligne 3: salaire cumulé (dynamique)
# -------------------------------
colA, colB = st.columns(2)

with colA:
    totalA = salaire_cumule(poolA if 'poolA' in locals() else None, saison, joueursA if 'joueursA' in locals() else [])
    st.metric("Salaire cumulé A", formater_argent(totalA))

with colB:
    totalB = salaire_cumule(poolB if 'poolB' in locals() else None, saison, joueursB if 'joueursB' in locals() else [])
    st.metric("Salaire cumulé B", formater_argent(totalB))



# -------------------------------
# Ligne 4: Essayer cet échange (règle de +/- 5%)
# -------------------------------
st.divider()
st.subheader("Validation de l'échange")

clique = st.button("Essayer cet échange")

if clique:
    # Vérifications de base
    if equipeA == "" or equipeB == "":
        st.warning("Veuillez d'abord sélectionner les deux équipes.")
    elif not joueursA or not joueursB:
        st.warning("Veuillez sélectionner au moins un joueur de chaque équipe.")
    else:
        # Recalculer les totaux au clic
        totalA = salaire_cumule(poolA if 'poolA' in locals() else None, saison, joueursA)
        totalB = salaire_cumule(poolB if 'poolB' in locals() else None, saison, joueursB)

        if totalA <= 0 or totalB <= 0:
            st.info("Les joueurs sélectionnés doivent avoir un salaire pour la saison choisie.")
        else:
            diff_pct = abs(totalA - totalB) / max(totalA, totalB)

            # Afficher les métriques dans 3 colonnes propres
            col1, col2, col3 = st.columns(3)
            col1.metric("Équipe A", formater_argent(totalA))
            col2.metric("Équipe B", formater_argent(totalB))
            col3.metric("Différence", f"{diff_pct:.2%}")

            # Vérification de la règle métier
            if diff_pct <= 0.05:
                st.success(" L'échange est valide selon la règle de correspondance des salaires de ±5%.")
            else:
                # Afficher les plages acceptables
                a_min, a_max = int(totalA * 0.95), int(totalA * 1.05)
                b_min, b_max = int(totalB * 0.95), int(totalB * 1.05)
                st.markdown(
                    f"""
                <div style="background-color:#ffe6e6; padding:15px; border-radius:10px; border:1px solid #ff4d4d;">
                    <b> Échange invalide: les totaux diffèrent de plus de 5%.</b><br><br>
                    • Pour correspondre à l'<b>Équipe A</b>: le total de l'Équipe B doit être entre
                    <span style="color:#d9534f;">{formater_argent(a_min)}</span> et <span style="color:#d9534f;">{formater_argent(a_max)}</span><br>
                    • Pour correspondre à l'<b>Équipe B</b>: le total de l'Équipe A doit être entre
                    <span style="color:#d9534f;">{formater_argent(b_min)}</span> et <span style="color:#d9534f;">{formater_argent(b_max)}</span>
                </div>
                """,
                    unsafe_allow_html=True
                )