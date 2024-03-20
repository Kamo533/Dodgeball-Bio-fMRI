import matplotlib.pyplot as plt
import numpy as np

from LogInterpreter import *

# TODO:
# marker start/slutt
# sørge for like mange punkter før og etter event, gjort, men bør sjekke fortsatt funker ved spill start/slutt

def setEventInOrigo(event_pos : list, movement_pos : list) -> list:
    return [(x-event_pos[0][0], y-event_pos[1][0], rotation) for x, y, rotation in movement_pos]

def rotate(origin, old_x, old_y):
    """
    Rotate points by a given slope around a given origin.

    The slope should be a number.
    """
    x, y = old_x, old_y

    a, k = np.polyfit(x, y, 1) # approksimates y = x * a + k
    ox, oy = origin

    n = 0

    while n == 0 or (np.abs(a) > 0.1 and n < 10):
        x, y = [], []
        angle = -np.arctan(a)

        if len(old_x) == len(old_y):
            num_points = len(old_x)

            for i in range(num_points):
                px, py = old_x[i], old_y[i]

                x.append(ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy))
                y.append(oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy))

        a, k = np.polyfit(x, y, 1) # approksimates y = x * a + k
        old_x, old_y = x, y
        ox, oy = [0, 0]
        n += 1

        print(f"Running with a:{a} and n:{n}")

    # x, y = [], []
    # if len(old_x) == len(old_y):
    #     num_points = len(old_x)
    #     angle = -np.arctan(a)

    #     for i in range(num_points):
    #         px, py = old_x[i], old_y[i]

    #         x.append(ox + np.cos(angle) * (px - ox) - np.sin(angle) * (py - oy))
    #         y.append(oy + np.sin(angle) * (px - ox) + np.cos(angle) * (py - oy))


    print(f"End with a:{a} and n:{n}")
    return x, y

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
    

    interval = 4 # num points before and after event

    h_plot  = 5
    v_plot = 3

    tot_num_events = 0
    for g in range(games.numGames()):
        game_events = games.games[g].player_data.filterByEventType(event)
        tot_num_events += len(game_events)
    print(f"Total number of events: {tot_num_events}")


    for i in range(6,7):
        print(games.games[i])
        fig, axs = plt.subplots(v_plot, h_plot)

        fig.suptitle(event)
        
        # create subplots
        game_events = games.games[i].player_data.filterByEventType(event)
        print(f"Num events in game {i}: {len(game_events)}")
        game_events = game_events[:h_plot*v_plot]


        for e in range(len(game_events)):
            time_interval = timedelta(0, (interval+2)*0.1)
            pos = games.games[i].pos_data.getGamePos(game_events[e].timestamp - time_interval, game_events[e].timestamp + time_interval)
            event_pos_both = games.games[i].getEventPos(game_events[e].timestamp)
            pos = pos[pos.index(event_pos_both)-interval:pos.index(event_pos_both)+interval+1]

            blue_owner = True if "Blue" in game_events[e].event_type else False

            event_pos = [event_pos_both.pos_blue_x if blue_owner else event_pos_both.pos_purple_x], [event_pos_both.pos_blue_y if blue_owner else event_pos_both.pos_purple_y]
            agent_pos = setEventInOrigo(event_pos=event_pos, movement_pos=games.games[i].pos_data.positionList(blue_owner, pos))

            axs[e//h_plot, e % h_plot].set_title(("Human" if blue_owner else games.games[i].game_type)) # f"{game_events[e].timestamp}" +
            axs[e//h_plot, e % h_plot].axis(xmin=-6,xmax=6, ymin=-6,ymax=6)

            # Plot linear reg
            x = np.array([x for x, _, _ in agent_pos])
            y = np.array([y for _, y, _ in agent_pos])
            x_new = x[:,np.newaxis]
            a, k = np.polyfit(x, y, 1) # approksimates y = x * a + k
            axs[e//h_plot, e % h_plot].plot([x for x, _, _ in agent_pos], [x * a + k for x, _, _ in agent_pos], 'r-')

            x, y = rotate([0,0], x, y)

            a2, k2 = np.polyfit(x, y, 1) # approksimates y = x * a2 + k2
            axs[e//h_plot, e % h_plot].plot([x for x, _, _ in agent_pos], [x * a2 + k2 for x, _, _ in agent_pos], 'g-')

            axs[e//h_plot, e % h_plot].plot(x, y, "-o", color="#522bbd") # Plot movement
            axs[e//h_plot, e % h_plot].plot([x[0]], [y[0]], marker="v", color="#93FF9E") # Plot start movement
            axs[e//h_plot, e % h_plot].plot([0], [0], marker="X", color="#fca55d") # Plot event


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


# possible_events = [
#     "BlueThrewBall", "PurpleThrewBall", "ThrewBall",
#     "BluePickedUpBall", "PurplePickedUpBall", "PickedUpBall",
#     "HitBlue", "HitPurple", "Hit",
#     "BlueDash", "PurpleDash", "Dash",
# ]
plotEvent("PickedUpBall", experiment_games)