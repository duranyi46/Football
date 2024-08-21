import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch, FontManager, Sbopen
import pandas as pd

def plot_match_goals(match_id):
    plt.style.use('ggplot')

    parser = Sbopen()
    # For bundesliga 2023/2024
    df_match = parser.match(competition_id=9, season_id=281)

    # Get the lineup for the match
    df_lineup = parser.lineup(match_id)
    df_lineup = df_lineup[['player_id', 'jersey_number', 'team_name']].copy()

    # Extract home and away team names
    home_team_name = df_match.loc[df_match['match_id'] == match_id]['home_team_name'].values[0]
    away_team_name = df_match.loc[df_match['match_id'] == match_id]['away_team_name'].values[0]

    # Get event data for the match
    df, related, freeze, tactics = parser.event(match_id)

    # Filter shots and goals for home and away teams
    df_shots_home = df[(df.type_name == 'Shot') & (df.team_name == home_team_name)].copy()
    df_shots_away = df[(df.type_name == 'Shot') & (df.team_name == away_team_name)].copy()
    df_goals_home = df_shots_home[df_shots_home.outcome_name == 'Goal']['id'].copy()
    df_goals_away = df_shots_away[df_shots_away.outcome_name == 'Goal']['id'].copy()
    df_goals = pd.concat([df_goals_home, df_goals_away]).reset_index(drop=True)

    # Iterate over each goal and create plots
    for i, goal_id in enumerate(df_goals, start=1):
        df_freeze_frame = freeze[freeze.id == goal_id].copy()
        df_shot_event = df[df.id == goal_id].dropna(axis=1, how='all').copy()

        # Add the jersey number
        df_freeze_frame = df_freeze_frame.merge(df_lineup, how='left', on='player_id')

        # Setup the pitch
        pitch = VerticalPitch(half=True, goal_type='box', pad_bottom=-20)
        fig, axs = pitch.grid(figheight=8, endnote_height=0, title_height=0.1, title_space=0.02, axis=False, grid_height=0.83)

        # Plot all players
        pitch.scatter(df_freeze_frame[df_freeze_frame['teammate']].x, df_freeze_frame[df_freeze_frame['teammate']].y, 
                      s=600, c='#727cce', label='Teammate', ax=axs['pitch'])
        pitch.scatter(df_freeze_frame[~df_freeze_frame['teammate'] & (df_freeze_frame.position_name != 'Goalkeeper')].x,
                      df_freeze_frame[~df_freeze_frame['teammate'] & (df_freeze_frame.position_name != 'Goalkeeper')].y,
                      s=600, c='#5ba965', label='Opponent', ax=axs['pitch'])
        pitch.scatter(df_freeze_frame[df_freeze_frame.position_name == 'Goalkeeper'].x,
                      df_freeze_frame[df_freeze_frame.position_name == 'Goalkeeper'].y,
                      s=600, c='#c15ca5', label='Goalkeeper', ax=axs['pitch'])

        # Plot the shot
        pitch.scatter(df_shot_event.x, df_shot_event.y, marker='football', s=600, ax=axs['pitch'], label='Shooter', zorder=1.2)
        pitch.lines(df_shot_event.x, df_shot_event.y, df_shot_event.end_x, df_shot_event.end_y, comet=True, label='Shot', color='#cb5a4c', ax=axs['pitch'])

        # Plot the angle to the goal
        pitch.goal_angle(df_shot_event.x, df_shot_event.y, ax=axs['pitch'], alpha=0.2, zorder=1.1, color='#cb5a4c', goal='right')

        # FontManager for Google font (Roboto)
        robotto_regular = FontManager()

        # Plot the jersey numbers (excluding NaN labels)
        for j, label in enumerate(df_freeze_frame.jersey_number):
            if pd.notna(label):  # Only annotate if the jersey number is not NaN
                pitch.annotate(label, (df_freeze_frame.x[j], df_freeze_frame.y[j]), va='center', ha='center', color='white', fontproperties=robotto_regular.prop, fontsize=15, ax=axs['pitch'])

        # Add a legend and title
        legend = axs['pitch'].legend(loc='center left', labelspacing=1.5)
        for text in legend.get_texts():
            text.set_fontproperties(robotto_regular.prop)
            text.set_fontsize(20)
            text.set_va('center')

        axs['title'].text(0.5, 0.5, f'{df_shot_event.player_name.iloc[0]}\n{home_team_name} vs. {away_team_name}', va='center', ha='center', color='black', fontproperties=robotto_regular.prop, fontsize=25)

        # Save the plot with a unique name
        plt.savefig(f'match_goal_{i}.png', dpi=300)
        plt.close()  # Close the plot to avoid display issues when generating multiple plots

