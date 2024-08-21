import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch, VerticalPitch, Sbopen
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def plot_pass_flow(match_id):
    parser = Sbopen()

    # Load match data
    df, related, freeze, tactics = parser.event(match_id)
    df_match = parser.match(competition_id=9, season_id=281)
    
    # Extract home and away team names
    home_team_name = df_match.loc[df_match['match_id'] == match_id]['home_team_name'].values[0]
    away_team_name = df_match.loc[df_match['match_id'] == match_id]['away_team_name'].values[0]

    # Filter passes and merge with tactics
    df = df[df.type_name == 'Pass']
    df = df[['x', 'y', 'end_x', 'end_y', "player_name", "pass_recipient_name", "team_name", "minute", 'player_id']]
    tactics = tactics[['jersey_number', 'player_id']]
    df_merged = pd.merge(df, tactics[['jersey_number', 'player_id']], on='player_id', how='left')
    
    # Keep only last names
    df_merged['player_name'] = df_merged['player_name'].str.split().str[-1]
    df_merged['pass_recipient_name'] = df_merged['pass_recipient_name'].str.split().str[-1]

    # Separate data for home and away teams
    df_home_pass = df_merged[df_merged.team_name == home_team_name]
    df_away_pass = df_merged[df_merged.team_name == away_team_name]

    # Check player play time and filter top 11 players for home team
    home_player_df = df_merged[df_merged.team_name == home_team_name].groupby('player_name').agg({'minute': [min, max]}).reset_index()
    home_player_df = pd.concat([home_player_df['player_name'], home_player_df['minute']], axis=1)
    home_player_df['minutes_played'] = home_player_df['max'] - home_player_df['min']
    home_player_df = home_player_df.sort_values('minutes_played', ascending=False)
    home_player_name = home_player_df.player_name[:11].tolist()
    df_home_pass = df_home_pass[df_home_pass.player_name.isin(home_player_name)]
    df_home_pass = df_home_pass[df_home_pass.pass_recipient_name.isin(home_player_name)]

    # Check player play time and filter top 11 players for away team
    away_player_df = df_merged[df_merged.team_name == away_team_name].groupby('player_name').agg({'minute': [min, max]}).reset_index()
    away_player_df = pd.concat([away_player_df['player_name'], away_player_df['minute']], axis=1)
    away_player_df['minutes_played'] = away_player_df['max'] - away_player_df['min']
    away_player_df = away_player_df.sort_values('minutes_played', ascending=False)
    away_player_name = away_player_df.player_name[:11].tolist()
    df_away_pass = df_away_pass[df_away_pass.player_name.isin(away_player_name)]
    df_away_pass = df_away_pass[df_away_pass.pass_recipient_name.isin(away_player_name)]

    # Calculate positions for home team
    scatter_home_df = pd.DataFrame()
    for i, name in enumerate(df_home_pass["player_name"].unique()):
        passx = df_home_pass.loc[df_home_pass["player_name"] == name]["x"].to_numpy()
        recx = df_home_pass.loc[df_home_pass["pass_recipient_name"] == name]["end_x"].to_numpy()
        passy = df_home_pass.loc[df_home_pass["player_name"] == name]["y"].to_numpy()
        recy = df_home_pass.loc[df_home_pass["pass_recipient_name"] == name]["end_y"].to_numpy()
        scatter_home_df.at[i, "player_name"] = name
        scatter_home_df.at[i, "x"] = np.mean(np.concatenate([passx, recx]))
        scatter_home_df.at[i, "y"] = np.mean(np.concatenate([passy, recy]))
        scatter_home_df.at[i, "no"] = df_home_pass.loc[df_home_pass["player_name"] == name].count().iloc[0]
        scatter_home_df.at[i, "jersey_number"] = df_home_pass.loc[df_home_pass["player_name"] == name]['jersey_number'].iloc[0]
        scatter_home_df['jersey_number'] = scatter_home_df['jersey_number'].astype(int)
    scatter_home_df['marker_size'] = (scatter_home_df['no'] / scatter_home_df['no'].max() * 1500)

    # Calculate positions for away team
    scatter_away_df = pd.DataFrame()
    for i, name in enumerate(df_away_pass["player_name"].unique()):
        passx = df_away_pass.loc[df_away_pass["player_name"] == name]["x"].to_numpy()
        recx = df_away_pass.loc[df_away_pass["pass_recipient_name"] == name]["end_x"].to_numpy()
        passy = df_away_pass.loc[df_away_pass["player_name"] == name]["y"].to_numpy()
        recy = df_away_pass.loc[df_away_pass["pass_recipient_name"] == name]["end_y"].to_numpy()
        scatter_away_df.at[i, "player_name"] = name
        scatter_away_df.at[i, "x"] = np.mean(np.concatenate([passx, recx]))
        scatter_away_df.at[i, "y"] = np.mean(np.concatenate([passy, recy]))
        scatter_away_df.at[i, "no"] = df_away_pass.loc[df_away_pass["player_name"] == name].count().iloc[0]
        scatter_away_df.at[i, "jersey_number"] = df_away_pass.loc[df_away_pass["player_name"] == name]['jersey_number'].iloc[0]
        scatter_away_df['jersey_number'] = scatter_away_df['jersey_number'].astype(int)
    scatter_away_df['marker_size'] = (scatter_away_df['no'] / scatter_away_df['no'].max() * 1500)

    # Calculate edge width for home team
    df_home_pass["pair_key"] = df_home_pass.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
    lines_home_df = df_home_pass.groupby(["pair_key"]).x.count().reset_index()
    lines_home_df.rename({'x': 'pass_count'}, axis='columns', inplace=True)
    lines_home_df = lines_home_df[lines_home_df['pass_count'] > 5]

    # Calculate edge width for away team
    df_away_pass["pair_key"] = df_away_pass.apply(lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
    lines_away_df = df_away_pass.groupby(["pair_key"]).x.count().reset_index()
    lines_away_df.rename({'x': 'pass_count'}, axis='columns', inplace=True)
    lines_away_df = lines_away_df[lines_away_df['pass_count'] > 5]

    # Plot for home team
    pitch = VerticalPitch(pitch_type='statsbomb', line_color='white', pitch_color='#2B2B2B', linewidth=1, goal_type='box',
                          axis=False, label=False, tick=False)
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
    pitch.scatter(scatter_home_df.x, scatter_home_df.y, s=scatter_home_df.marker_size, color='#272822',
                  edgecolors='#EDBB00', linewidth=3, alpha=1, ax=ax["pitch"], zorder=3)

    for i, row in scatter_home_df.iterrows():
        pitch.annotate(row.player_name, xy=(row.x + 6, row.y), c='white', va='center', ha='center', size=6,
                       weight="bold", ax=ax["pitch"], zorder=4, bbox=dict(facecolor='#272822', alpha=1,
                       edgecolor='#272822', boxstyle='round,pad=0.4'))
        pitch.annotate(row.jersey_number, xy=(row.x, row.y - 0.1), c='white', va='center', ha='center', size=8,
                       weight="bold", ax=ax["pitch"], zorder=4)

    for i, row in lines_home_df.iterrows():
        player1 = row["pair_key"].split("_")[0]
        player2 = row['pair_key'].split("_")[1]
        player1_x = scatter_home_df.loc[scatter_home_df["player_name"] == player1]['x'].iloc[0]
        player1_y = scatter_home_df.loc[scatter_home_df["player_name"] == player1]['y'].iloc[0]
        player2_x = scatter_home_df.loc[scatter_home_df["player_name"] == player2]['x'].iloc[0]
        player2_y = scatter_home_df.loc[scatter_home_df["player_name"] == player2]['y'].iloc[0]
        num_passes = row["pass_count"]
        line_width = (num_passes / lines_home_df['pass_count'].max() * 8)
        alpha = max(num_passes / lines_home_df['pass_count'].max(), 0.2)
        alpha = max(alpha, 0.5)
        pitch.lines(player1_x, player1_y, player2_x, player2_y, alpha=alpha,
                    lw=line_width, zorder=2, color="#EDBB00", ax=ax["pitch"])

    fig.text(s=home_team_name + " Passing Networks", x=0.5, y=0.98, ha="center", color="white",
             fontsize=18, fontproperties="fantasy")
    plt.savefig('home_pass_flow.png', dpi=300, bbox_inches='tight')

    # Plot for away team
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
    pitch.scatter(scatter_away_df.x, scatter_away_df.y, s=scatter_away_df.marker_size, color='#272822',
                  edgecolors='#EDBB00', linewidth=3, alpha=1, ax=ax["pitch"], zorder=3)

    for i, row in scatter_away_df.iterrows():
        pitch.annotate(row.player_name, xy=(row.x + 6, row.y), c='white', va='center', ha='center', size=6,
                       weight="bold", ax=ax["pitch"], zorder=4, bbox=dict(facecolor='#272822', alpha=1,
                       edgecolor='#272822', boxstyle='round,pad=0.4'))
        pitch.annotate(row.jersey_number, xy=(row.x, row.y - 0.1), c='white', va='center', ha='center', size=8,
                       weight="bold", ax=ax["pitch"], zorder=4)

    for i, row in lines_away_df.iterrows():
        player1 = row["pair_key"].split("_")[0]
        player2 = row['pair_key'].split("_")[1]
        player1_x = scatter_away_df.loc[scatter_away_df["player_name"] == player1]['x'].iloc[0]
        player1_y = scatter_away_df.loc[scatter_away_df["player_name"] == player1]['y'].iloc[0]
        player2_x = scatter_away_df.loc[scatter_away_df["player_name"] == player2]['x'].iloc[0]
        player2_y = scatter_away_df.loc[scatter_away_df["player_name"] == player2]['y'].iloc[0]
        num_passes = row["pass_count"]
        line_width = (num_passes / lines_away_df['pass_count'].max() * 8)
        alpha = max(num_passes / lines_away_df['pass_count'].max(), 0.2)
        alpha = max(alpha, 0.5)
        pitch.lines(player1_x, player1_y, player2_x, player2_y, alpha=alpha,
                    lw=line_width, zorder=2, color="#EDBB00", ax=ax["pitch"])

    fig.text(s=away_team_name + " Passing Networks", x=0.5, y=0.98, ha="center", color="white",
             fontsize=18, fontproperties="fantasy")
    plt.savefig('away_pass_flow.png', dpi=300, bbox_inches='tight')

    plt.show()

# Example usage
plot_pass_flow(3895302)





