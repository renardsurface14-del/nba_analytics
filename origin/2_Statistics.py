import pandas as pd
import streamlit as st
import plotly.express as px

# Run with: py -m streamlit run test.py
st.set_page_config(layout="wide")

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



# Load data
df_reg_season_players = pd.read_excel("data/df_reg_season_players_filtered.xlsx")
df_playoff_players = pd.read_excel("data/df_playoff_players_filtered.xlsx")

# -------------------------------
# Title
# -------------------------------
st.markdown(
    "<h1 style='text-align: center;'>NBA 2024-25 Statistics</h1>", 
    unsafe_allow_html=True
)
st.markdown(
    "<h3 style='text-align: center; color: gray;'>Numbers Behind the Highlights</h3>", 
    unsafe_allow_html=True
)

# -------------------------------
# Filters in one row
# -------------------------------
col1, col2, col3, col4 = st.columns([1, 1, 1, 1], gap="large")

with col1:
    metric_filter = st.selectbox(
        "Choose a view", 
        ["Leaders", "Top 30", "Full Data"],
        key="metric_filter"
    )

with col2:
    season_filter = st.radio(
        "Season Type", 
        ["Regular Season", "Playoffs"], 
        horizontal=True,
        key="season_filter"
    )
with col3:
    stat_mode = st.radio(
        "Stat Mode", 
        ["Per Game", "Total"], 
        horizontal=True,
        key="stat_mode"
    )

# Conditionally display Display Mode
if metric_filter in ["Top 30", "Full Data"]:
    view_mode = "Table"  # force Table for Top 30
else:
    with col4:
        view_mode = st.radio(
            "Display Mode", 
            ["Table", "Bar Chart"], 
            horizontal=True,
            key="view_mode"
        )



# -------------------------------
# Select the right dataset
# -------------------------------

df = df_reg_season_players if season_filter == "Regular Season" else df_playoff_players

df = df[(df["GP"] > 10) & (df["MIN_PG"] > 10)]

# -------------------------------
# Utility: Custom Bar Plot
# -------------------------------
def custom_bar_chart(data, col_name, title):
    # Sort data descending for correct order
    data_sorted = data.sort_values(by=col_name, ascending=False)

    fig = px.bar(
        data_sorted,
        x=col_name,
        y="PLAYER_NAME",
        orientation="h",
        color="TEAM",
        title=title,
        text=col_name,
        category_orders={"PLAYER_NAME": data_sorted["PLAYER_NAME"].tolist()}  # enforce order
    )

    fig.update_traces(
        texttemplate="%{text}",
        textposition="inside",   # label stays inside the bar
        insidetextanchor="end",  # align it to the end of the bar
        textfont=dict(color="white", size=14, family="Arial")
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
# Functions
# -------------------------------
def show_offense(df, label, mode, view_mode):
    suffix = "_PG" if mode == "Per Game" else ""
    st.markdown(f"## 🏀 Offensive Statistics ({label} - {mode})")

    stats = {
        "Points": "PTS",
        "Assists": "AST",
        "3-Pointers Made": "FG3M",
        "Free Throws Made": "FTM"
    }

    col1, col2 = st.columns(2)
    for (title, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        top_data = df[["PLAYER_NAME", "TEAM", col_name + suffix]].sort_values(by=col_name + suffix, ascending=False).head(5)
        if view_mode == "Table":
            col.markdown(f"### {title} {mode}")
            col.dataframe(top_data, hide_index=True, use_container_width=True)
        else:
            fig = custom_bar_chart(top_data, col_name + suffix, f"{title}")
            col.plotly_chart(fig, use_container_width=True)

def show_defense(df, label, mode, view_mode):
    suffix = "_PG" if mode == "Per Game" else ""
    st.markdown(f"## 🛡️ Defensive Statistics ({label} - {mode})")

    stats = {
        "Total Rebounds": "REB",
        "Defensive Rebounds": "DREB",
        "Blocks": "BLK",
        "Steals": "STL"
    }

    col1, col2 = st.columns(2)
    for (title, col_name), col in zip(stats.items(), [col1, col2, col1, col2]):
        top_data = df[["PLAYER_NAME", "TEAM", col_name + suffix]].sort_values(by=col_name + suffix, ascending=False).head(5)
        if view_mode == "Table":
            col.markdown(f"### {title} {mode}")
            col.dataframe(top_data, hide_index=True, use_container_width=True)
        else:
            fig = custom_bar_chart(top_data, col_name + suffix, f"{title}")
            col.plotly_chart(fig, use_container_width=True)
            
# -------------------------------
# Display According to Filters
# -------------------------------
if metric_filter == "Leaders":
    show_offense(df, season_filter, stat_mode, view_mode)
    st.divider()
    show_defense(df, season_filter, stat_mode, view_mode)

elif metric_filter == "Top 30":
    stat_choice = st.selectbox(
        "Select a statistic",
        [
            "Points",
            "Assists",
            "Total Rebounds",
            "Offensive Rebounds",
            "Defensive Rebounds",
            "Minutes",
            "3-Pointers Made",
            "Free Throws Made",
            "Blocks",
            "Steals",
            "Turnovers",
        ]
    )
    suffix = "_PG" if stat_mode == "Per Game" else ""
    stat_map = {
        "Points": "PTS",
        "Assists": "AST",
        "Total Rebounds": "REB",
        "Offensive Rebounds": "OREB",
        "Defensive Rebounds": "DREB",
        "Minutes": "MIN",
        "3-Pointers Made": "FG3M",
        "Free Throws Made": "FTM",
        "Blocks": "BLK",
        "Steals": "STL",
        "Turnovers": "TOV",
    }

    chosen_col = stat_map[stat_choice] + suffix
    top30 = (
        df[["PLAYER_NAME", "TEAM", chosen_col]]
        .sort_values(by=chosen_col, ascending=False)
        .head(30)
    )

    st.markdown(f"## 🔥 Top 30 {stat_choice} ({stat_mode}) - {season_filter}")
    st.dataframe(top30, hide_index=True, use_container_width=True)

elif metric_filter == "Full Data":
    st.markdown(f"## 📊 {season_filter} — Full Data (Field Parameter Style)")

    # Step 1: available columns except PLAYER_NAME
    available_fields = [col for col in df.columns if col != "PLAYER_NAME"]

    # Step 2: Add "Select All" option at the top
    multiselect_options = ["Select All"] + available_fields

    # Step 3: multiselect widget
    selected_fields = st.multiselect(
        "Select columns to display",
        options=multiselect_options,
        default=available_fields[:3]
    )

    # Step 4: If "Select All" is selected → replace with all fields
    if "Select All" in selected_fields:
        selected_fields = available_fields  # all real fields

    # Step 5: show table
    if selected_fields:
        df_view = df[["PLAYER_NAME"] + selected_fields]
        st.dataframe(df_view, hide_index=True, use_container_width=True)
    else:
        st.info("Please select at least one column to display. The Player Name is selected by default")