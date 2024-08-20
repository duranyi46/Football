from mplsoccer import Sbopen, FontManager, VerticalPitch
import matplotlib.pyplot as plt

def plot_shot_scatter(match_id):
    parser = Sbopen()

    # Get match data
    df_match = parser.match(competition_id=9, season_id=281)
    home_team_name = df_match.loc[df_match['match_id'] == match_id]['home_team_name'].values[0]
    away_team_name = df_match.loc[df_match['match_id'] == match_id]['away_team_name'].values[0]
    
    # Get event data
    df, related, freeze, tactics = parser.event(match_id)
    df_shots_home = df[(df.type_name == 'Shot') & (df.team_name == home_team_name)].copy()
    df_shots_away = df[(df.type_name == 'Shot') & (df.team_name == away_team_name)].copy()

    # Load custom font
    fm_rubik = FontManager('https://raw.githubusercontent.com/google/fonts/main/ofl/'
                           'rubikmonoone/RubikMonoOne-Regular.ttf')

    # Plot for Home Team
    df_goals_home = df_shots_home[df_shots_home.outcome_name == 'Goal'].copy()
    df_non_goal_shots_home = df_shots_home[df_shots_home.outcome_name != 'Goal'].copy()
    pitch = VerticalPitch(pad_bottom=0.5, half=True, goal_type='box', goal_alpha=0.8, 
                          pitch_color='grass', line_color='white')
    fig, ax = pitch.draw(figsize=(12, 10))

    # Plot non-goal shots
    pitch.scatter(df_non_goal_shots_home.x, df_non_goal_shots_home.y,
                  s=(df_non_goal_shots_home.shot_statsbomb_xg * 1900) + 100,
                  edgecolors='black',
                  c='white',
                  marker='football',
                  ax=ax)

    # Plot goal shots
    pitch.scatter(df_goals_home.x, df_goals_home.y,
                  s=(df_goals_home.shot_statsbomb_xg * 1900) + 100,
                  edgecolors='red',
                  linewidths=0.6,
                  c='white',
                  marker='football',
                  ax=ax)

    # Add text
    ax.text(x=40, y=80, s=f'{home_team_name} shots\nversus {away_team_name}',
            size=30, fontproperties=fm_rubik.prop, color=pitch.line_color,
            va='center', ha='center')

    # Save the plot
    plt.savefig('home_team_scatter.png')

    # Plot for Away Team
    df_goals_away = df_shots_away[df_shots_away.outcome_name == 'Goal'].copy()
    df_non_goal_shots_away = df_shots_away[df_shots_away.outcome_name != 'Goal'].copy()
    pitch = VerticalPitch(pad_bottom=0.5, half=True, goal_type='box', goal_alpha=0.8, 
                          pitch_color='grass', line_color='white')
    fig, ax = pitch.draw(figsize=(12, 10))

    # Plot non-goal shots
    pitch.scatter(df_non_goal_shots_away.x, df_non_goal_shots_away.y,
                  s=(df_non_goal_shots_away.shot_statsbomb_xg * 1900) + 100,
                  edgecolors='black',
                  c='white',
                  marker='football',
                  ax=ax)

    # Plot goal shots
    pitch.scatter(df_goals_away.x, df_goals_away.y,
                  s=(df_goals_away.shot_statsbomb_xg * 1900) + 100,
                  edgecolors='red',
                  linewidths=0.6,
                  c='white',
                  marker='football',
                  ax=ax)

    # Add text
    ax.text(x=40, y=80, s=f'{away_team_name} shots\nversus {home_team_name}',
            size=30, fontproperties=fm_rubik.prop, color=pitch.line_color,
            va='center', ha='center')

    # Save the plot
    plt.savefig('away_team_scatter.png')

# Example usage:
plot_shot_scatter(3895302)
