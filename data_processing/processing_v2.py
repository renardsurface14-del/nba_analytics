# processing_v2.py
# -*- coding: utf-8 -*-
"""Second pass: add/normalize player positions, preview, then overwrite Excel."""

import time
import pandas as pd
import streamlit as st
from nba_api.stats.static import teams
from nba_api.stats.endpoints import commonteamroster

# -------------------------------
# Config
# -------------------------------
SEASON   = "2024-25"
REG_PATH = "data/df_reg_season_players.xlsx"
PO_PATH  = "data/df_playoff_players.xlsx"

st.set_page_config(layout="wide")
st.title("Processing v2 — Add Player Positions")

# -------------------------------
# Load existing data
# -------------------------------
df_reg = pd.read_excel(REG_PATH)
df_po  = pd.read_excel(PO_PATH)

st.dataframe(df_reg)
st.dataframe(df_po)

# -------------------------------
# Fetch roster positions (retry + throttle, still simple)
# -------------------------------
pos_frames = []
failed = []

team_list = teams.get_teams()
progress = st.progress(0)
total = len(team_list)

for i, t in enumerate(team_list, start=1):
    team_id = t["id"]
    name = t.get("full_name", t.get("abbreviation", str(team_id)))

    got = False
    for attempt in range(4):  # try up to 4 times
        try:
            roster = commonteamroster.CommonTeamRoster(
                team_id=team_id, season=SEASON, timeout=90
            ).get_data_frames()[0]
            pos_frames.append(roster[["PLAYER_ID", "PLAYER", "POSITION"]])
            got = True
            break
        except Exception:
            time.sleep(0.8 * (attempt + 1))  # short backoff: 0.8s, 1.6s, 2.4s
    if not got:
        failed.append(name)

    time.sleep(0.5)  # gentle throttle between teams
    progress.progress(i / total)

if failed:
    st.warning(f"Could not fetch roster for: {', '.join(failed)}")

if not pos_frames:
    st.error("No roster data fetched after retries. Try again in a minute.")
    st.stop()

df_positions = pd.concat(pos_frames, ignore_index=True)

# Keep only what's needed and ensure one row per player
df_positions = (
    df_positions[["PLAYER_ID", "POSITION"]]
    .dropna(subset=["PLAYER_ID"])
    .drop_duplicates(subset=["PLAYER_ID"], keep="last")
)

# -------------------------------
# Merge positions (left join on PLAYER_ID)
# -------------------------------
df_reg = df_reg.merge(df_positions, how="left", on="PLAYER_ID", validate="m:1")
df_po  = df_po.merge(df_positions, how="left", on="PLAYER_ID", validate="m:1")

#st.dataframe(df_reg)
#st.dataframe(df_po)


# If the merge produced POSITION_x / POSITION_y, rename the one from roster to POS
if "POSITION_x" in df_reg.columns:
    df_reg.rename(columns={"POSITION_x": "POS"}, inplace=True)
if "POSITION_x" in df_po.columns:
    df_po.rename(columns={"POSITION_x": "POS"}, inplace=True)

# Drop any leftover POSITION_y to avoid confusion
for df_ in (df_reg, df_po):
    if "POSITION_y" in df_.columns:
        df_.drop(columns=["POSITION_y"], inplace=True)



# -------------------------------
# Map to friendly labels
# -------------------------------
position_map = {
    "G":   "Guard",
    "F":   "Forward",
    "C":   "Center",
    "G-F": "Guard",          # your chosen rule
    "F-G": "Small Forward",  # your chosen rule
    "F-C": "Power Forward",
    "C-F": "Center",
}

# Make sure POS is a Series (single column) before mapping
df_reg["POSITION"] = df_reg["POS"].map(position_map).fillna("Unknown")
df_po["POSITION"]  = df_po["POS"].map(position_map).fillna("Unknown")

"""# -------------------------------
# Overwrite Excel files
# -------------------------------
df_reg.to_excel(REG_PATH, index=False)
df_po.to_excel(PO_PATH, index=False)

st.success("Excel files updated with POS (raw) and POSITION (friendly)")
st.write(f"- {REG_PATH}")
st.write(f"- {PO_PATH}")

st.dataframe(df_po[["PLAYER_NAME","TEAM","POS","POSITION"]])
st.dataframe(df_reg[["PLAYER_NAME","TEAM","POS","POSITION"]])"""
