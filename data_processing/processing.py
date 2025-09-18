# -*- coding: utf-8 -*-
"""NBA GM Tool"""

# -------------------------------
# Imports
# -------------------------------
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import commonteamroster, playercareerstats, leaguedashplayerstats
#import requests
#from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
#import duckdb as db
st.title("Data Processing")

# -------------------------------
# Get NBA Teams
# -------------------------------
nba_teams = teams.get_teams()
df_teams = pd.DataFrame(nba_teams)
#print(df_teams.head())


# -------------------------------
# Get Regular Season Player Stats
# -------------------------------
df_players = leaguedashplayerstats.LeagueDashPlayerStats(season='2024-25').get_data_frames()[0]



# Filter only NBA teams (avoid non-NBA teams if any)
teams_nba = [
    'ATL', 'BOS', 'BKN', 'CHA', 'CHI', 'CLE', 'DAL', 'DEN', 'DET',
    'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM', 'MIA', 'MIL', 'MIN',
    'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHX', 'POR', 'SAC', 'SAS',
    'TOR', 'UTA', 'WAS'
]
df_nba = df_players[df_players["TEAM_ABBREVIATION"].isin(teams_nba)].copy()
df_nba = df_nba[(df_nba["PLAYER_NAME"].notna()) & (df_nba["PLAYER_NAME"] != "None")]
df_nba.reset_index(drop=True, inplace=True)

#st.dataframe(df_nba)


# Final NBA players DataFrame
df_reg_season_players = df_nba[['PLAYER_ID','PLAYER_NAME','NICKNAME', 'TEAM_ABBREVIATION',
                         'AGE', 'GP', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA',
                         'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 
                         'FT_PCT', 'PTS', 'OREB', 'DREB', 'REB', 'AST', 'TOV',
                         'STL', 'BLK', 'PLUS_MINUS']]





### evolution creer une fonction 
# Add per-game columns for main stats
df_reg_season_players['MIN_PG'] = (df_reg_season_players['MIN'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['FGM_PG'] = (df_reg_season_players['FGM'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['FGA_PG'] = (df_reg_season_players['FGA'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['FG3M_PG'] = (df_reg_season_players['FG3M'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['FG3A_PG'] = (df_reg_season_players['FG3A'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['FTM_PG'] = (df_reg_season_players['FTM'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['FTA_PG'] = (df_reg_season_players['FTA'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['PTS_PG'] = (df_reg_season_players['PTS'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['OREB_PG'] = (df_reg_season_players['OREB'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['DREB_PG'] = (df_reg_season_players['DREB'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['REB_PG'] = (df_reg_season_players['REB'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['AST_PG'] = (df_reg_season_players['AST'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['TOV_PG'] = (df_reg_season_players['TOV'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['STL_PG'] = (df_reg_season_players['STL'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['BLK_PG'] = (df_reg_season_players['BLK'] / df_reg_season_players['GP']).round(1)
df_reg_season_players['PLUS_MINUS_PG'] = (df_reg_season_players['PLUS_MINUS'] / df_reg_season_players['GP']).round(1)


#st.dataframe(df_reg_season_players[df_reg_season_players["PLAYER_NAME"]=="Jayson Tatum"])


df_reg_season_players.to_excel("df_reg_season_players.xlsx", index=False)


# -------------------------------
# Get Playoff Player Stats
# -------------------------------
df_playoff = leaguedashplayerstats.LeagueDashPlayerStats(
    season='2024-25',
    season_type_all_star='Playoffs'
).get_data_frames()[0]

# Keep only NBA players with valid names
df_playoff = df_playoff[df_playoff["TEAM_ABBREVIATION"].isin(teams_nba)].copy()
df_playoff = df_playoff[(df_playoff["PLAYER_NAME"].notna()) & (df_playoff["PLAYER_NAME"] != "None")]
df_playoff.reset_index(drop=True, inplace=True)

# Final Playoff players DataFrame
df_playoff_players = df_playoff[['PLAYER_ID','PLAYER_NAME','NICKNAME', 'TEAM_ABBREVIATION',
                         'AGE', 'GP', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA',
                         'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 
                         'FT_PCT', 'PTS', 'OREB', 'DREB', 'REB', 'AST', 'TOV',
                         'STL', 'BLK', 'PLUS_MINUS']]

### evolution creer une fonction 
# Add per-game columns for main stats
df_playoff_players['MIN_PG'] = (df_playoff_players['MIN'] / df_playoff_players['GP']).round(1)
df_playoff_players['FGM_PG'] = (df_playoff_players['FGM'] / df_playoff_players['GP']).round(1)
df_playoff_players['FGA_PG'] = (df_playoff_players['FGA'] / df_playoff_players['GP']).round(1)
df_playoff_players['FG3M_PG'] = (df_playoff_players['FG3M'] / df_playoff_players['GP']).round(1)
df_playoff_players['FG3A_PG'] = (df_playoff_players['FG3A'] / df_playoff_players['GP']).round(1)
df_playoff_players['FTM_PG'] = (df_playoff_players['FTM'] / df_playoff_players['GP']).round(1)
df_playoff_players['FTA_PG'] = (df_playoff_players['FTA'] / df_playoff_players['GP']).round(1)
df_playoff_players['PTS_PG'] = (df_playoff_players['PTS'] / df_playoff_players['GP']).round(1)
df_playoff_players['OREB_PG'] = (df_playoff_players['OREB'] / df_playoff_players['GP']).round(1)
df_playoff_players['DREB_PG'] = (df_playoff_players['DREB'] / df_playoff_players['GP']).round(1)
df_playoff_players['REB_PG'] = (df_playoff_players['REB'] / df_playoff_players['GP']).round(1)
df_playoff_players['AST_PG'] = (df_playoff_players['AST'] / df_playoff_players['GP']).round(1)
df_playoff_players['TOV_PG'] = (df_playoff_players['TOV'] / df_playoff_players['GP']).round(1)
df_playoff_players['STL_PG'] = (df_playoff_players['STL'] / df_playoff_players['GP']).round(1)
df_playoff_players['BLK_PG'] = (df_playoff_players['BLK'] / df_playoff_players['GP']).round(1)
df_playoff_players['PLUS_MINUS_PG'] = (df_playoff_players['PLUS_MINUS'] / df_playoff_players['GP']).round(1)



# Save to Excel
df_playoff_players.to_excel("df_playoff_players.xlsx", index=False)


# -------------------------------
# Add TEAM column with full team names
# -------------------------------

nba_teams_dict = {
    'GSW': 'Golden State Warriors',
    'PHI': 'Philadelphia 76ers',
    'DEN': 'Denver Nuggets',
    'HOU': 'Houston Rockets',
    'BOS': 'Boston Celtics',
    'MIL': 'Milwaukee Bucks',
    'DAL': 'Dallas Mavericks',
    'PHO': 'Phoenix Suns',
    'NYK': 'New York Knicks',
    'LAL': 'Los Angeles Lakers',
    'LAC': 'Los Angeles Clippers',
    'SAC': 'Sacramento Kings',
    'CLE': 'Cleveland Cavaliers',
    'UTA': 'Utah Jazz',
    'ATL': 'Atlanta Hawks',
    'MIN': 'Minnesota Timberwolves',
    'IND': 'Indiana Pacers',
    'NOP': 'New Orleans Pelicans',
    'MEM': 'Memphis Grizzlies',
    'TOR': 'Toronto Raptors',
    'ORL': 'Orlando Magic',
    'DET': 'Detroit Pistons',
    'OKC': 'Oklahoma City Thunder',
    'BRK': 'Brooklyn Nets',
    'CHO': 'Charlotte Hornets',
    'MIA': 'Miami Heat',
    'SAS': 'San Antonio Spurs',
    'POR': 'Portland Trail Blazers',
    'WAS': 'Washington Wizards',
    'CHI': 'Chicago Bulls'
}


nba_teams_dict_inverse = {
    'Golden State Warriors': 'GSW',
    'Philadelphia 76ers': 'PHI',
    'Denver Nuggets': 'DEN',
    'Houston Rockets': 'HOU',
    'Boston Celtics': 'BOS',
    'Milwaukee Bucks': 'MIL',
    'Dallas Mavericks': 'DAL',
    'Phoenix Suns': 'PHO',
    'New York Knicks': 'NYK',
    'Los Angeles Lakers': 'LAL',
    'Los Angeles Clippers': 'LAC',
    'Sacramento Kings': 'SAC',
    'Cleveland Cavaliers': 'CLE',
    'Utah Jazz': 'UTA',
    'Atlanta Hawks': 'ATL',
    'Minnesota Timberwolves': 'MIN',
    'Indiana Pacers': 'IND',
    'New Orleans Pelicans': 'NOP',
    'Memphis Grizzlies': 'MEM',
    'Toronto Raptors': 'TOR',
    'Orlando Magic': 'ORL',
    'Detroit Pistons': 'DET',
    'Oklahoma City Thunder': 'OKC',
    'Brooklyn Nets': 'BRK',
    'Charlotte Hornets': 'CHO',
    'Miami Heat': 'MIA',
    'San Antonio Spurs': 'SAS',
    'Portland Trail Blazers': 'POR',
    'Washington Wizards': 'WAS',
    'Chicago Bulls': 'CHI'
}


df_reg_season_players.insert(
    2,  # position after TEAM_ABBREVIATION
    "TEAM",
    df_reg_season_players["TEAM_ABBREVIATION"].apply(lambda abv: nba_teams_dict.get(abv, "Unknown"))
)

df_playoff_players.insert(
    2,
    "TEAM",
    df_playoff_players["TEAM_ABBREVIATION"].apply(lambda abv: nba_teams_dict.get(abv, "Unknown"))
)

#Show a preview
#st.dataframe(df_reg_season_players[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM', 'PTS_PG']].head())
#st.dataframe(df_playoff_players[['PLAYER_NAME', 'TEAM_ABBREVIATION', 'TEAM', 'PTS_PG']].head())


# -------------------------------
# Load Excel Sources
# -------------------------------
df_western_conf_standing = pd.read_excel("excel_source/western_conf_standing.xlsx")
df_eastern_conf_standing = pd.read_excel("excel_source/eastern_conf_standing.xlsx")
df_nba_team_playoff_stats_pg = pd.read_excel("excel_source/nba_team_playoff_stats_pg.xlsx")
df_nba_team_playoff_advanced_stats = pd.read_excel("excel_source/nba_team_playoff_advanced_stats.xlsx")
df_nba_players_salaries = pd.read_excel("excel_source/nba_players_salaries.xlsx")
df_nba_team_reg_season_ratings = pd.read_excel("excel_source/nba_team_reg_season_ratings.xlsx")

#st.dataframe(df_nba_team_reg_season_ratings)



# Champion history
df_nba_champion = pd.read_excel('excel_source/nba_champion.xlsx')

#st.dataframe(df_nba_champion)


df_nba_champion.drop("Unnamed: 5", axis=1, inplace=True)

# Filter advanced stats columns
df_nba_team_playoff_advanced_stats = df_nba_team_playoff_advanced_stats[['Rk', 'Tm', 'Age', 'W', 'L', 
                                                                         'W/L%', 'ORtg', 'DRtg', 'NRtg', 
                                                                         'Pace', 'TS%', 'eFG%']]
df_nba_team_reg_season_ratings = df_nba_team_reg_season_ratings[['Rk', 'Team', 'Conf', 'Div', 
                                                                 'W', 'L', 'W/L%', 'ORtg', 'DRtg','NRtg']]

#st.dataframe(df_nba_players_salaries)


# Re-indexing
dfs = [df_nba_players_salaries, df_nba_team_playoff_stats_pg,
       df_nba_team_playoff_advanced_stats, df_nba_team_reg_season_ratings]
for df in dfs:
    df.set_index("Rk", inplace=True)

#st.dataframe(df_nba_team_playoff_advanced_stats)



# Rename columns (replace spaces with _ and uppercase)
dfs = [df_western_conf_standing, df_eastern_conf_standing, df_nba_team_playoff_stats_pg,
       df_nba_team_playoff_advanced_stats, df_nba_players_salaries, 
       df_nba_team_reg_season_ratings, df_nba_champion]
for df in dfs:
    df.columns = [col.replace(" ", "_").upper() for col in df.columns]


#st.dataframe(df_western_conf_standing)



# Add Playoff Team flag
df_western_conf_standing.insert(1, "PLAYOFF_TEAM",
    df_western_conf_standing["WESTERN_CONFERENCE"].apply(lambda x: "*" in str(x)))
df_eastern_conf_standing.insert(1, "PLAYOFF_TEAM",
    df_eastern_conf_standing["EASTERN_CONFERENCE"].apply(lambda x: "*" in str(x)))

#st.dataframe(df_eastern_conf_standing)


#
# Remove * from team names
df_western_conf_standing["WESTERN_CONFERENCE"] = df_western_conf_standing["WESTERN_CONFERENCE"].str.replace("*","")
df_eastern_conf_standing["EASTERN_CONFERENCE"] = df_eastern_conf_standing["EASTERN_CONFERENCE"].str.replace("*","")

#st.dataframe(df_eastern_conf_standing)


# Rename TEAM column
df_western_conf_standing.rename(columns={"WESTERN_CONFERENCE": "TEAM"}, inplace=True)
df_eastern_conf_standing.rename(columns={"EASTERN_CONFERENCE": "TEAM"}, inplace=True)
df_nba_team_playoff_stats_pg.rename(columns={"TM": "TEAM"}, inplace=True)
df_nba_team_playoff_advanced_stats.rename(columns={"TM": "TEAM"}, inplace=True)



# -------------------------------
# Add missing TEAM or TM columns
# -------------------------------

# 1) TEAM -> add TM
dfs_with_team = [df_western_conf_standing,
                 df_eastern_conf_standing,
                 df_nba_team_playoff_stats_pg,
                 df_nba_team_playoff_advanced_stats,
                 df_nba_team_reg_season_ratings]

for df in dfs_with_team:
    df.insert(1, "TM", df["TEAM"].apply(lambda x: nba_teams_dict_inverse.get(x, "Unknown")))

# 2) TM -> add TEAM
df_nba_players_salaries.insert(
    1, 
    "TEAM", 
    df_nba_players_salaries["TM"].apply(lambda x: nba_teams_dict.get(x, "Unknown"))
)

# 3) Special case: Champions
df_nba_champion.insert(
    4, 
    "TM_CHAMP", 
    df_nba_champion["CHAMPION"].apply(lambda x: nba_teams_dict_inverse.get(x, "Unknown"))
)
df_nba_champion.insert(
    5, 
    "TM_RUNNER_UP", 
    df_nba_champion["RUNNER-UP"].apply(lambda x: nba_teams_dict_inverse.get(x, "Unknown"))
)

# 4) Ensure consistency for regular season and playoffs
df_reg_season_players.insert(
    2,
    "TM",
    df_reg_season_players["TEAM_ABBREVIATION"].apply(lambda abv: abv)  # already has abv
)

df_playoff_players.insert(
    2,
    "TM",
    df_playoff_players["TEAM_ABBREVIATION"].apply(lambda abv: abv)
)


st.dataframe(df_nba_players_salaries)

# -------------------------------
# Export Final DataFrames
# -------------------------------
dataframes = {
    "data/df_western_conf_standing.xlsx": df_western_conf_standing,
    "data/df_eastern_conf_standing.xlsx": df_eastern_conf_standing,
    "data/df_nba_team_playoff_stats_pg.xlsx": df_nba_team_playoff_stats_pg,
    "data/df_nba_team_playoff_advanced_stats.xlsx": df_nba_team_playoff_advanced_stats,
    "data/df_nba_players_salaries.xlsx": df_nba_players_salaries,
    "data/df_nba_team_reg_season_ratings.xlsx": df_nba_team_reg_season_ratings,
    "data/df_nba_champion.xlsx": df_nba_champion,
    "data/df_reg_season_players.xlsx": df_reg_season_players,
    "data/df_playoff_players.xlsx": df_playoff_players
}

for filename, df in dataframes.items():
    df.to_excel(filename, index=False)
    print(f"Exported: {filename}")
