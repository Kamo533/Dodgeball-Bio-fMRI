from LogInterpreter import *


def plotEvent(event : str, log_folders : list):
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
    

    


experiments_folders = [
    "Assets//Dodgeball//Logs//fMRI_2024-02-27",
    "Assets//Dodgeball//Logs//fMRI_2024-03-05"
]

unused_games = [ # games with 1 or more games that still can't be used
    "2024-02-27_13-12-12"
]



# print(exploreFolder("Assets//Dodgeball//Logs//fMRI_2024-03-05"))
# getUniqueDates(exploreFolder("Assets//Dodgeball//Logs//fMRI_2024-03-05"))
    
plotEvent("ThrewBall", experiments_folders)

experiment_games = GameDataContainer(experiments_folders, unused_games)
print(experiment_games)
print(f"Number of game sessions:{len(experiment_games.games)}")
