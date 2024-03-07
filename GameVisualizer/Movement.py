import matplotlib.pyplot as plt
import numpy as np

from LogInterpreter import *


def plotEvent(event : str, games : GameDataContainer):
    """
    Possible events from GameLogger: 
        "BlueThrewBall", "PurpleThrewBall", 
        "BluePickedUpBall", "PurplePickedUpBall", 
        "HitBlue", "HitPurple", 
        "BlueDash", "PurpleDash", 
        "ResetScene", "S", "WinScreenStart", "GameEnd", "FinishCountDown"
    """
    possible_events = [
        "BlueThrewBall", "PurpleThrewBall", "ThrewBall",
        "BluePickedUpBall", "PurplePickedUpBall", "PickedUpBall",
        "HitBlue", "HitPurple", "Hit",
        "BlueDash", "PurpleDash", "Dash",
    ]

    event_index = -1

    try:
        event_index = possible_events.index(event)
    except ValueError:
        raise Exception(f"{event} is not a valid event to plot. Must be one of {possible_events}")
    

    interval = 2

    h_plot  = 4
    v_plot = 3

    for i in range(2):
        print(games.games[i])
        fig, axs = plt.subplots(v_plot, h_plot)
        
        # create subplots
        game_events = games.games[i].player_data.filterByEventType(event)[:h_plot*v_plot]

        for e in range(len(game_events)):
            pos = games.games[i].pos_data.getGamePos(game_events[e].timestamp - timedelta(0, interval), game_events[e].timestamp + timedelta(0, interval))

            blue_owner = True if "Blue" in game_events[e].event_type else False

            agent_pos = games.games[i].pos_data.positionList(blue_owner, pos)

            axs[e//h_plot, e % h_plot].scatter([x for x, _, _ in agent_pos], [y for _, y, _ in agent_pos])
            axs[e//h_plot, e % h_plot].set_title(game_events[e].event_type)
            # marker "X"
            event_pos = games.games[i].getEventPos(game_events[e].timestamp)
            axs[e//h_plot, e % h_plot].scatter([event_pos.pos_blue_x if blue_owner else event_pos.pos_purple_x], [event_pos.pos_blue_y if blue_owner else event_pos.pos_purple_y], marker="X")

            # print(f"event time:{game_events[e].timestamp}, closest pos time:{ games.games[i].getEventPos(game_events[e].timestamp)}")
    
        plt.show()

            

    


experiments_folders = [
    "Assets//Dodgeball//Logs//fMRI_2024-02-27",
    "Assets//Dodgeball//Logs//fMRI_2024-03-05"
]

unused_games = [ # games with 1 or more games that still can't be used
    "2024-02-27_13-12-12"
]


experiment_games = GameDataContainer(experiments_folders, unused_games)
# print(experiment_games)
print(f"Number of game sessions:{len(experiment_games.games)}")

plotEvent("PickedUpBall", experiment_games)