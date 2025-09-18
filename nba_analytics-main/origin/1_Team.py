# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from nav import navbar

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="Team", layout="wide")

# -------------------------------
# Show navbar
# -------------------------------
# --- Top navbar (official) ---
c1, c2, c3, c4,c5 = st.columns(5)
with c1: st.page_link("home.py",                   label="🏠 Home")
with c2: st.page_link("pages/1_Team.py",           label="🏀 Team")
with c3: st.page_link("pages/2_Statistics.py",     label="📊 Statistics")
with c4: st.page_link("pages/3_Champ_Historic.py", label="🏆 Historic")
with c5: st.page_link("pages/4_Trade_Machine.py",  label="💸 Trade Machine")


# -------------------------------
# Load Data
# -------------------------------
df_west = pd.read_excel("data/df_western_conf_standing.xlsx")
df_east = pd.read_excel("data/df_eastern_conf_standing.xlsx")
df_team_ratings = pd.read_excel("data/df_nba_team_reg_season_ratings.xlsx")
df_reg_players = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
df_po_players = pd.read_excel("data/df_playoff_players_filtered.xlsx")
df_salaries = pd.read_excel("data/df_nba_players_salaries.xlsx")


# -------------------------------
# Apply additional filters for player quality
# -------------------------------
df_reg_players = df_reg_players[(df_reg_players["GP"] > 10) & (df_reg_players["MIN_PG"] > 10)]
df_po_players = df_po_players[(df_po_players["GP"] > 10) & (df_po_players["MIN_PG"] > 10)]

# -------------------------------
# Function
# -------------------------------
def render_kpi(df, value_col, title):
    if df.empty or value_col not in df.columns or df[value_col].dropna().empty:
        st.info(f"No data for {title}.")
        return

    idx = df[value_col].idxmax()
    row = df.loc[idx]
    val = float(row[value_col])
    player_name = str(row.get("PLAYER_NAME", "Unknown"))
    team_name = str(row.get("TEAM", row.get("TEAM_ABBREVIATION", "")))

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

def render_kpi_box(title, value_text, subtitle=""):
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


# -------------------------------
# Title
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>🏀 NBA TEAM 2024-25 Overview</h1>",
    unsafe_allow_html=True
)

# -------------------------------
# Global Team Filter
# -------------------------------
team_options = sorted(df_reg_players["TEAM"].dropna().unique())
selected_team = st.selectbox("Select a Team", team_options, index=0, key="team_filter")

# -------------------------------
# Build combined standings with flags + rank
# -------------------------------
df_west_local = df_west.copy()
df_east_local = df_east.copy()

df_west_local["CONF"] = "West"
df_east_local["CONF"] = "East"

# If your standings are already sorted, rank is row order
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

# Lookup selected team rank
team_row = df_standings[df_standings["TEAM"] == selected_team]
if not team_row.empty:
    conf = team_row.iloc[0]["CONF"]
    rank = int(team_row.iloc[0]["RANK"])
    st.markdown(f"**Conference:** {conf} — **Rank:** #{rank}")
else:
    st.info("Selected team not found in standings.")




# -------------------------------
# General Data
# -------------------------------
season_filter = st.radio(
        "Season Type",
        ["Regular Season", "Playoffs"],
        horizontal=True,
        key="season_filter_team"
    )

# Select correct dataset for the season
df = df_reg_players if season_filter == "Regular Season" else df_po_players

# Apply global team filter
df = df[df["TEAM"] == selected_team]

# If Playoffs selected but team did not make playoffs, stop this tab gracefully
if season_filter == "Playoffs":
    row = df_standings[df_standings["TEAM"] == selected_team]
    is_po = bool(row["PLAYOFF_TEAM"].iloc[0]) if not row.empty else False
    if not is_po:
        st.warning(f"{selected_team} did not make the playoffs in 2024-25 — no playoff player stats to display.")
        st.stop()

st.markdown(f"### Team Stats — {selected_team}")
st.markdown("## 📌 General Stats")

# -------------------------------
# Tabs (Bookmarks)
# -------------------------------
tab_stats, tab_salaries = st.tabs(["📊 Team Stats", "💰 Salaries"])



# ===============================
# 📊 I. TEAM STATS
# ===============================
with tab_stats:
    

    # --- First row KPIs ---
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi(df, "PTS_PG", "Points per Game")
    with c2:
        render_kpi(df, "REB_PG", "Rebounds per Game")
    with c3:
        render_kpi(df, "AST_PG", "Assists per Game")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Second row KPIs ---
    c4, c5, c6 = st.columns(3)
    with c4:
        render_kpi(df, "STL_PG", "Steals per Game")
    with c5:
        render_kpi(df, "BLK_PG", "Blocks per Game")
    with c6:
        render_kpi(df, "TOV_PG", "Turnovers per Game")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    
    # --------------------------------
    # Full Team — Field Parameter Style
    # --------------------------------
    st.markdown("## Full Team")

    # Default columns (only keep those that actually exist)
    default_cols = [c for c in ["TEAM", "PLAYER_NAME", "PTS_PG", "AST_PG", "REB_PG", "MIN_PG"] if c in df.columns]

    # Additional fields you can add on top of defaults
    additional_fields = [c for c in df.columns if c not in default_cols]

    # Multiselect with "Select All"
    multiselect_options = ["Select All"] + additional_fields
    selected_extra = st.multiselect(
        "Add columns to display",
        options=multiselect_options,
        default=[],
        key="team_full_fields"
    )

    # Expand "Select All"
    if "Select All" in selected_extra:
        selected_extra = additional_fields

    # Final column list to show
    cols_to_show = default_cols + selected_extra

    if cols_to_show:
        st.dataframe(df[cols_to_show], hide_index=True, use_container_width=True)
    else:
        st.info("No columns selected. Please choose at least one.")


# ===============================
# 💰 II. SALARIES
# ===============================

# -------------------------------
# Unpivot Salaries
# -------------------------------
year_cols = ["2025-26", "2026-27", "2027-28", "2028-29", "2029-30", "2030-31", "GUARANTEED"]

df_salaries_unpivoted = df_salaries.melt(
    id_vars=["PLAYER", "TEAM"],
    value_vars=year_cols,
    var_name="YEAR",
    value_name="SALARY"
)


# -------------------------------
# Join salaries (long) with players to get POSITION
# -------------------------------
df_players_slim = df_reg_players[["PLAYER_NAME", "TEAM", "POSITION","PTS_PG","AST_PG","REB_PG"]]#.drop_duplicates()
df_players_slim = df_players_slim.rename(columns={"PLAYER_NAME": "PLAYER"})

df_join = pd.merge(
    df_salaries_unpivoted,   # PLAYER, TEAM, YEAR, SALARY
    df_players_slim,         # PLAYER, TEAM, POSITION
    how="left",
    on=["PLAYER", "TEAM"]
)

# Add numeric salary column
df_join["SALARY_NUM"] = (
    df_join["SALARY"]
    .astype(str)
    .str.replace(r"[^0-9]", "", regex=True)
    .replace("", "0")
    .astype(int)
)

# ===============================
# 💰 Salaries (pie by position)
# ===============================
with tab_salaries:
    st.markdown(f"### Player Salaries — {selected_team}")



    all_years = sorted([y for y in df_salaries_unpivoted["YEAR"].dropna().unique() if str(y) != "GUARANTEED"])
    selected_year = st.selectbox("Select Season", all_years, index=0)

    df_team_year = df_join[(df_join["TEAM"] == selected_team) & (df_join["YEAR"] == selected_year)].copy()

    
    # ===============================
    # KPI cards for selected year
    # ===============================

    # KPI

    # --- 1) Compute KPI values from df_team_year (already filtered by TEAM + YEAR)
    team_total = int(df_team_year["SALARY_NUM"].sum())

    if not df_team_year.empty and df_team_year["SALARY_NUM"].max() > 0:
        top_row = df_team_year.loc[df_team_year["SALARY_NUM"].idxmax()]
        top_player = str(top_row["PLAYER"])
        top_salary = int(top_row["SALARY_NUM"])
    else:
        top_player, top_salary = "—", 0

    # “Value”: (PPG+APG+RPG) per $1M for this team & year
    df_val = df_team_year.copy()
    df_val[["PTS_PG","AST_PG","REB_PG"]] = df_val[["PTS_PG","AST_PG","REB_PG"]].fillna(0)
    df_val["salary_m"] = df_val["SALARY_NUM"].replace(0, pd.NA) / 1_000_000
    df_val["value_score"] = (df_val["PTS_PG"] + df_val["AST_PG"] + df_val["REB_PG"]) / df_val["salary_m"]

    if df_val["value_score"].dropna().empty:
        best_value_player, best_value_score = "—", 0.0
    else:
        best_row = df_val.loc[df_val["value_score"].idxmax()]
        best_value_player = str(best_row["PLAYER"])
        best_value_score  = float(best_row["value_score"])

    # --- ) Show the three KPI cards
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_box("Team Payroll", f"${team_total:,.0f}", f"{selected_team} — {selected_year}")
    with c2:
        render_kpi_box("Top-Paid Player", f"${top_salary:,.0f}", top_player)
    with c3:
        render_kpi_box("Best Value (PPG+APG+RPG per $1M)", f"{best_value_score:.1f}", best_value_player)


        


    # PIE CHART

    # ✅ Group by position with numeric salary
    df_pie = (
        df_team_year.groupby("POSITION", dropna=False, as_index=False)["SALARY_NUM"]
        .sum()
        .sort_values("SALARY_NUM", ascending=False)
    )

    if df_pie["SALARY_NUM"].sum() == 0 or df_pie.empty:
        st.info("No salary data available for this team/year.")
    else:
        fig = px.pie(
            df_pie,
            names="POSITION",
            values="SALARY_NUM",
            title=f"Total Salaries by Position — {selected_team} ({selected_year})",
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

        with st.expander("Show player rows for this season"):
            st.dataframe(
                df_team_year[["PLAYER", "POSITION", "SALARY"]],
                hide_index=True,
                use_container_width=True
            )