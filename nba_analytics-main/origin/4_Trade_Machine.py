# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
from nav import navbar


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
# Page config
# -------------------------------
st.set_page_config(page_title="Trade Machine", layout="wide")

st.title("💸 NBA Trade Machine")

st.write("Select two teams and players to simulate a trade. Salaries will be compared.")



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
# Function
# -------------------------------
def cumulative_salary(pool_df: pd.DataFrame, season: str, selected_players: list[str]) -> int:
    """Return cumulative salary (already numeric) for selected players."""
    if not selected_players or pool_df is None or season not in pool_df.columns:
        return 0
    return int(pool_df.loc[pool_df["PLAYER"].isin(selected_players), season].sum())

def format_money(amount: int) -> str:
    return f"${amount:,.0f}"

# Step 1: Count how many valid contract years each player has
year_cols = ["2025-26","2026-27","2027-28","2028-29","2029-30","2030-31"]

# Replace placeholders like "None", "-", "" with NaN
df_salaries[year_cols] = df_salaries[year_cols].replace(
    ["None", "", "-", "—"], pd.NA
)

# Create new column with the number of non-null contract years
df_salaries["contract_years"] = df_salaries[year_cols].notna().sum(axis=1)

# Step 2: Create a clean subset of df_reg_players with only relevant columns
# Rename PLAYER_NAME -> PLAYER to align with df_salaries
stat_cols = ["POSITION","AST_PG","BLK_PG","AGE","FG_PCT","FG3_PCT",
             "GP","MIN","PLUS_MINUS","PTS_PG","REB_PG","STL_PG","TOV_PG"]

df_reg_subset = (
    df_reg_players
      .rename(columns={"PLAYER_NAME": "PLAYER"})
      [["PLAYER","TEAM"] + stat_cols]
)

# Step 3: Merge salaries and player stats into one dataframe
df_joins = df_salaries.merge(df_reg_subset, on=["PLAYER","TEAM"], how="left")

# Preprocess salary columns: keep only digits, convert to int
for col in year_cols + ["GUARANTEED"]:
    if col in df_joins.columns:
        df_joins[col] = (
            df_joins[col]
            .astype(str)
            .str.replace(r"[^0-9]", "", regex=True)
            .replace("", "0")
            .astype(int)
        )

# -------------------------------
# Row 1: season selector
# -------------------------------
SEASONS = ["2025-26","2026-27","2027-28","2028-29","2029-30","2030-31"]
season = st.selectbox("Select season", SEASONS)

# -------------------------------
# Row 2: team + player selection with roster preview
# -------------------------------
colA, colB = st.columns(2)

team_list = sorted(df_joins["TEAM"].dropna().unique())

with colA:
    st.subheader("Team A")
    teamA = st.selectbox("Choose Team A", [""] + team_list, key="teamA")
    playersA = []
    if teamA == "":
        st.write("Please select a team.")
    else:
        poolA = df_joins[df_joins["TEAM"] == teamA].copy()

        # Display: PLAYER, contract_years, Salary (selected season), GUARANTEED
        displayA = poolA[["PLAYER", "contract_years", season, "GUARANTEED"]].copy()
        displayA = displayA.rename(columns={season: "Salary"})
        displayA["Salary"] = displayA["Salary"].map(format_money)
        displayA["GUARANTEED"] = displayA["GUARANTEED"].map(format_money)
        st.dataframe(displayA, hide_index=True, use_container_width=True)

        # Player selection (names only; details are shown in the table)
        playersA = st.multiselect("Select players from Team A", poolA["PLAYER"].tolist(), key="playersA")

with colB:
    st.subheader("Team B")
    # Remove Team A from options if selected
    team_options_B = [""] + [t for t in team_list if t != teamA]
    teamB = st.selectbox("Choose Team B", team_options_B, key="teamB")
    playersB = []
    if teamB == "":
        st.write("Please select a team.")
    else:
        poolB = df_joins[df_joins["TEAM"] == teamB].copy()

        displayB = poolB[["PLAYER", "contract_years", season, "GUARANTEED"]].copy()
        displayB = displayB.rename(columns={season: "Salary"})
        displayB["Salary"] = displayB["Salary"].map(format_money)
        displayB["GUARANTEED"] = displayB["GUARANTEED"].map(format_money)
        st.dataframe(displayB, hide_index=True, use_container_width=True)

        playersB = st.multiselect("Select players from Team B", poolB["PLAYER"].tolist(), key="playersB")


# -------------------------------
# Row 3: cumulative salary (dynamic)
# -------------------------------
colA, colB = st.columns(2)

with colA:
    totalA = cumulative_salary(poolA if 'poolA' in locals() else None, season, playersA if 'playersA' in locals() else [])
    st.metric("Cumulative salary A", format_money(totalA))

with colB:
    totalB = cumulative_salary(poolB if 'poolB' in locals() else None, season, playersB if 'playersB' in locals() else [])
    st.metric("Cumulative salary B", format_money(totalB))



# -------------------------------
# Row 4: Try this trade (+/- 5% rule)
# -------------------------------
st.divider()
st.subheader("Trade validation")

clicked = st.button("✅ Try this trade")

if clicked:
    # Basic guards
    if teamA == "" or teamB == "":
        st.warning("Please select both teams first.")
    elif not playersA or not playersB:
        st.warning("Please select at least one player from each team.")
    else:
        # Recompute totals on click
        totalA = cumulative_salary(poolA if 'poolA' in locals() else None, season, playersA)
        totalB = cumulative_salary(poolB if 'poolB' in locals() else None, season, playersB)

        if totalA <= 0 or totalB <= 0:
            st.info("Selected players must have a salary for the chosen season.")
        else:
            diff_pct = abs(totalA - totalB) / max(totalA, totalB)

            # Show metrics in 3 clean columns
            col1, col2, col3 = st.columns(3)
            col1.metric("Team A", format_money(totalA))
            col2.metric("Team B", format_money(totalB))
            col3.metric("Difference", f"{diff_pct:.2%}")

            # Business rule check
            if diff_pct <= 0.05:
                st.success("✅ Trade is valid under the ±5% salary match rule.")
            else:
                # Show acceptable ranges
                a_lower, a_upper = int(totalA * 0.95), int(totalA * 1.05)
                b_lower, b_upper = int(totalB * 0.95), int(totalB * 1.05)
                st.markdown(
                    f"""
                <div style="background-color:#ffe6e6; padding:15px; border-radius:10px; border:1px solid #ff4d4d;">
                    <b>❌ Trade invalid: totals differ by more than 5%.</b><br><br>
                    • To match <b>Team A</b>: Team B total must be between 
                    <span style="color:#d9534f;">{format_money(a_lower)}</span> and <span style="color:#d9534f;">{format_money(a_upper)}</span><br>
                    • To match <b>Team B</b>: Team A total must be between 
                    <span style="color:#d9534f;">{format_money(b_lower)}</span> and <span style="color:#d9534f;">{format_money(b_upper)}</span>
                </div>
                """,
                    unsafe_allow_html=True
                )