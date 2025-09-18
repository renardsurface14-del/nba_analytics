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
df_nba_champion = pd.read_excel("data/df_nba_champion.xlsx")

st.markdown(
    "<h1 style='text-align: center;'>Champion Historic since 1976</h1>", 
    unsafe_allow_html=True
)


# -------------------------------
# Filters
# -------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    year_filter = st.selectbox(
        "Select Year", 
        ["All"] + sorted(df_nba_champion["YEAR"].unique().tolist(), reverse=True)
    )

with col2:
    champ_filter = st.selectbox(
        "Select Champion Team", 
        ["All"] + sorted(df_nba_champion["CHAMPION"].dropna().unique().tolist())
    )

with col3:
    runner_filter = st.selectbox(
        "Select Runner-Up Team", 
        ["All"] + sorted(df_nba_champion["RUNNER-UP"].dropna().unique().tolist())
    )

with col4:
    player_filter = st.selectbox(
        "Select Player", 
        ["All"] + sorted(
            pd.concat([
                df_nba_champion["FINALS_MVP"].dropna(),
                df_nba_champion["POINTS"].dropna(),
                df_nba_champion["REBOUNDS"].dropna(),
                df_nba_champion["ASSISTS"].dropna()
            ]).unique().tolist()
        )
    )

# -------------------------------
# Apply Filters
# -------------------------------
filtered_df = df_nba_champion.copy()

if year_filter != "All":
    filtered_df = filtered_df[filtered_df["YEAR"] == year_filter]

if champ_filter != "All":
    filtered_df = filtered_df[filtered_df["CHAMPION"] == champ_filter]

if runner_filter != "All":
    filtered_df = filtered_df[filtered_df["TM_RUNNER_UP"] == runner_filter]

if player_filter != "All":
    mask = (
        filtered_df["FINALS_MVP"].str.contains(player_filter, na=False) |
        filtered_df["POINTS"].str.contains(player_filter, na=False) |
        filtered_df["REBOUNDS"].str.contains(player_filter, na=False) |
        filtered_df["ASSISTS"].str.contains(player_filter, na=False)
    )
    filtered_df = filtered_df[mask]

# -------------------------------
# Display Filtered Data
# -------------------------------
st.dataframe(filtered_df, hide_index=True, use_container_width=True)

# -------------------------------
# Utility: Custom Bar Plot
# -------------------------------
def custom_bar_chart(data, value_col, label_col, title, color_col=None):
    # Sort descending for largest values at top
    data_sorted = data.sort_values(by=value_col, ascending=False)

    fig = px.bar(
        data_sorted,
        x=value_col,
        y=label_col,
        orientation="h",
        title=title,
        text=value_col,
        color=color_col if color_col else None,
        category_orders={label_col: data_sorted[label_col].tolist()}
    )

    fig.update_traces(
        texttemplate="%{text}",
        textposition="inside",       # labels inside bars
        insidetextanchor="end",      # align to the end of bar
        textfont=dict(color="white", size=14, family="Arial")
    )

    fig.update_layout(
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        bargap=0.2,
        plot_bgcolor="white",
        showlegend=False,
        margin=dict(l=100, r=50, t=50, b=50)  # space for labels
    )

    return fig


# -------------------------------
# 1) Most Titles by Team (Top 10)
# -------------------------------
titles_count = (
    df_nba_champion.groupby("CHAMPION")
    .size()
    .reset_index(name="Titles")
    .sort_values(by="Titles", ascending=False)
    .head(10)
)

st.plotly_chart(custom_bar_chart(
    titles_count, "Titles", "CHAMPION", "🏆 Top 10 Teams by Titles", color_col="CHAMPION"
), use_container_width=True)


# -------------------------------
# 2) Most Finals MVP Awards by Player (Top 10)
# -------------------------------
mvp_count = (
    df_nba_champion.groupby("FINALS_MVP")
    .size()
    .reset_index(name="MVP Awards")
    .sort_values(by="MVP Awards", ascending=False)
    .head(10)
)

st.plotly_chart(
    custom_bar_chart(mvp_count, "MVP Awards", "FINALS_MVP", "🥇 Top 10 Finals MVP Award Winners", color_col="FINALS_MVP"),
    use_container_width=True
)

# -------------------------------
# 3) Most Finals Appearances by Team (Top 10)
# -------------------------------
team_appearances = (
    pd.concat([
        df_nba_champion[["CHAMPION"]].rename(columns={"CHAMPION": "Team"}),
        df_nba_champion[["RUNNER-UP"]].rename(columns={"RUNNER-UP": "Team"})
    ])
    .groupby("Team")
    .size()
    .reset_index(name="Appearances")
    .sort_values(by="Appearances", ascending=False)
    .head(10)
)

st.plotly_chart(
    custom_bar_chart(team_appearances, "Appearances", "Team", "📊 Top 10 Finals Appearances by Team", color_col="Team"),
    use_container_width=True
)