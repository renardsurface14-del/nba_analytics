# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from nav import navbar

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(page_title="NBA Dashboard", layout="wide")

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
df_players = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
df_salaries = pd.read_excel("data/df_nba_players_salaries.xlsx")


df_players = df_players[(df_players["GP"] > 10) & (df_players["MIN_PG"] > 10)]


# -------------------------------
# Title
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>🏀 NBA 2024-25 Overview</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<h4 style='text-align: center; color: gray;'>A Global Look at the League</h4>",
    unsafe_allow_html=True
)



# -------------------------------
# Tabs (bookmark-like navigation)
# -------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 Conference Standings",
    "⭐ Top Players",
    "📊 Team Ratings",
    "💰 Salaries"
])

# -------------------------------
# 1) Conference Standings
# -------------------------------
with tab1:
    st.markdown("## 🏆 Conference Standings")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Western Conference")
        st.dataframe(df_west, hide_index=True, use_container_width=True)
    with col2:
        st.markdown("### Eastern Conference")
        st.dataframe(df_east, hide_index=True, use_container_width=True)

# -------------------------------
# 2) Top Players
# -------------------------------
with tab2:
    st.markdown("## ⭐ Top 3 Players by Key Metrics")

    # Single-select team filter with "All teams" option
    all_teams = sorted(df_players["TEAM"].dropna().unique())
    team_choice = st.selectbox(
        "Team",
        options=["All teams"] + all_teams,
        index=0,
        key="top_players_team_filter_single"
    )

    # Apply local filter
    df_tp = df_players.copy()
    if team_choice != "All teams":
        df_tp = df_tp[df_tp["TEAM"] == team_choice]

    metrics = {
        "Points Per Game": "PTS_PG",
        "Rebounds Per Game": "REB_PG",
        "Assists Per Game": "AST_PG"
    }

    for label, col_name in metrics.items():
        if col_name not in df_tp.columns:
            st.warning(f"Column '{col_name}' not found in player data.")
            continue

        top3 = (
            df_tp[["PLAYER_NAME", "TEAM", col_name]]
            .sort_values(by=col_name, ascending=False)
            .head(3)
        )
        st.markdown(f"### {label}")
        st.dataframe(top3, hide_index=True, use_container_width=True)

# -------------------------------
# 3) Team Ratings
# -------------------------------
with tab3:
    st.markdown("## 📊 Team Performance Ratings (Top 10)")

    col1, col2, col3 = st.columns(3)

    # Offensive Rating (higher is better)
    with col1:
        st.markdown("### Offensive Rating")
        if "ORTG" in df_team_ratings.columns:
            off = df_team_ratings[["TEAM", "ORTG"]].sort_values(by="ORTG", ascending=False).head(10)
            st.dataframe(off, hide_index=True, use_container_width=True)
        else:
            st.warning("Column 'ORTG' not found in team ratings.")

    # Defensive Rating (lower is better → ascending)
    with col2:
        st.markdown("### Defensive Rating")
        if "DRTG" in df_team_ratings.columns:
            deff = df_team_ratings[["TEAM", "DRTG"]].sort_values(by="DRTG", ascending=True).head(10)
            st.dataframe(deff, hide_index=True, use_container_width=True)
        else:
            st.warning("Column 'DRTG' not found in team ratings.")

    # Net Rating (higher is better)
    with col3:
        st.markdown("### Net Rating")
        if "NRTG" in df_team_ratings.columns:
            net = df_team_ratings[["TEAM", "NRTG"]].sort_values(by="NRTG", ascending=False).head(10)
            st.dataframe(net, hide_index=True, use_container_width=True)
        else:
            st.warning("Column 'NRTG' not found in team ratings.")

# -------------------------------
# 4) Salaries — simple filters only
# -------------------------------

with tab4:
    st.markdown("## 💰 Salaries")

    # Team filter
    team_options = ["All teams"] + sorted(df_salaries["TEAM"].dropna().unique())
    team_sel = st.selectbox("Team", team_options, index=0)

    # Filter dataframe by selected team
    df_filtered = df_salaries.copy()
    if team_sel != "All teams":
        df_filtered = df_filtered[df_filtered["TEAM"] == team_sel]

    # Player filter (depends on filtered dataframe)
    player_options = ["All players"] + sorted(df_filtered["PLAYER"].dropna().unique())
    player_sel = st.selectbox("Player", player_options, index=0)

    # Apply player filter
    if player_sel != "All players":
        df_filtered = df_filtered[df_filtered["PLAYER"] == player_sel]

    # Display filtered table
    st.dataframe(df_filtered, hide_index=True, use_container_width=True)
