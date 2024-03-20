import matplotlib.pyplot as plt
import numpy as np

from LogInterpreter import *

# TODO:
# marker start/slutt
# sørge for like mange punkter før og etter event

def setEventInOrigo(event_pos : list, movement_pos : list) -> list:
    return [(x-event_pos[0][0], y-event_pos[1][0], rotation) for x, y, rotation in movement_pos]

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
    

    interval = 4.9 # num points before and after event

    h_plot  = 5
    v_plot = 3

    # tot_num_events = 0
    # for g in range(games.numGames()):
    #     game_events = games.games[g].player_data.filterByEventType(event)
    #     tot_num_events += len(game_events)
    # print(f"Total number of events: {tot_num_events}")


    for i in range(6,7):
        print(games.games[i])
        fig, axs = plt.subplots(v_plot, h_plot)

        fig.suptitle(event)
        
        # create subplots
        game_events = games.games[i].player_data.filterByEventType(event)
        print(f"Num events in game {i}: {len(game_events)}")
        game_events = game_events[:h_plot*v_plot]


        for e in range(len(game_events)):
            pos = games.games[i].pos_data.getGamePos(game_events[e].timestamp - timedelta(0, (interval)*0.1), game_events[e].timestamp + timedelta(0, (interval)*0.1))

            blue_owner = True if "Blue" in game_events[e].event_type else False

            # agent_pos = games.games[i].pos_data.positionList(blue_owner, pos)
            event_pos_both = games.games[i].getEventPos(game_events[e].timestamp)
            event_pos = [event_pos_both.pos_blue_x if blue_owner else event_pos_both.pos_purple_x], [event_pos_both.pos_blue_y if blue_owner else event_pos_both.pos_purple_y]
            agent_pos = setEventInOrigo(event_pos=event_pos, movement_pos=games.games[i].pos_data.positionList(blue_owner, pos))

            axs[e//h_plot, e % h_plot].scatter([x for x, _, _ in agent_pos], [y for _, y, _ in agent_pos])
            axs[e//h_plot, e % h_plot].set_title(("Human" if blue_owner else games.games[i].game_type)) # f"{game_events[e].timestamp}" +
            
            axs[e//h_plot, e % h_plot].scatter([0], [0])
            axs[e//h_plot, e % h_plot].axis(xmin=-5,xmax=5, ymin=-5,ymax=5)

        plt.show()

            

    


experiments_folders = [
    "Assets//Dodgeball//Logs//fMRI_2024-02-27",
    "Assets//Dodgeball//Logs//fMRI_2024-03-05",
    "Assets//Dodgeball//Logs//fMRI_2024-03-12",
    "Assets//Dodgeball//Logs//fMRI_2024-03-14"
]

unused_games = [ # games with 1 or more games that still can't be used
    "2024-02-27_13-12-12",
    "2024-03-14_12-13-05"
]


experiment_games = GameDataContainer(experiments_folders, unused_games)
# print(experiment_games)
print(f"Number of game sessions:{experiment_games.numGames()}")

plotEvent("ThrewBall", experiment_games)