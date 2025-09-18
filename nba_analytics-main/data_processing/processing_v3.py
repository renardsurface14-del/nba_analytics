# processing_v3.py
# -*- coding: utf-8 -*-
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Processing v3 — Filters", layout="wide")
st.title("Processing v3 — Clean Players")

# -------------------------------
# Load Data
# -------------------------------
REG_PATH = "data/df_reg_season_players.xlsx"
PO_PATH  = "data/df_playoff_players.xlsx"

df_reg = pd.read_excel(REG_PATH)
df_po  = pd.read_excel(PO_PATH)

# -------------------------------
# Simple filters
# -------------------------------
def clean_players(df):
    # Drop unknown positions
    if "POSITION" in df.columns:
        df = df[df["POSITION"] != "Unknown"]

    # Drop players with <= 5 minutes per game
    if "MIN_PG" in df.columns:
        df = df[df["MIN_PG"] > 5]

    return df

df_reg_clean = clean_players(df_reg)
df_po_clean  = clean_players(df_po)

# -------------------------------
# Save cleaned data
# -------------------------------
df_reg_clean.to_excel("data/df_reg_season_players_filtered.xlsx", index=False)
df_po_clean.to_excel("data/df_playoff_players_filtered.xlsx", index=False)

st.success("Filtered files saved!")
