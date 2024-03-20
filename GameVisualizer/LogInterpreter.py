from datetime import datetime, timedelta
import os


timestamp_format = "%H:%M:%S.%f"
date_format = "%Y-%m-%d_%H-%M-%S"


def getLogData(name, date, subfolder="") -> str:
    """
    Returns the log data from one log file from the time of date, as a string
    name - PlayerData , Position or Results
    """
    log_path = "Assets/Dodgeball/Logs/fMRI_" + date.split("_")[0] + subfolder

    part_path = ""
    if name == "PlayerData":
        part_path = "Player_Data"
    else:
        part_path = name
    full_path = log_path + "/" + name + "/GameLog_" + part_path + "_" + date + ".txt"

    f = open(full_path, "r")
    data = f.read()
    f.close()
    return data

def exploreFolder(path : str):
    """
    Explore a folder and all subfolders. Ignores .meta files.
 
    Parameters
    path : str
        the path to the folder to be explored
 
    Returns
    list
        path to all files under the folder at path
    """
    pot_folders = os.listdir(path)

    file_list = []

    for element in pot_folders:
        if ".meta" in element:
            continue

        new_element = path + "//" + element
        if "." in element:
            file_list.append(new_element)
        else:
            file_list.extend(exploreFolder(new_element))
    
    return file_list

def getUniqueDates(files_list : list):
    file_end_format = date_format + ".txt"
    dates = set()

    for file_path in files_list:
        dates.add(datetime.strptime(file_path[-23:], file_end_format))

    return dates


class PositionData:
    def __init__(self, pos_data: str) -> None:
        self.pos_list = []

        iterator = iter(pos_data.splitlines())
        next(iterator)  # Skip first line
        for pos_line in iterator:
            self.pos_list.append(self.Position(pos_line))

    class Position:
        def __init__(self, position_line) -> None:
            data = position_line.replace("(", "").replace(")", "").split(",")
            self.timestamp = datetime.strptime(data[0], timestamp_format)
            self.pos_blue_x = float(data[1])
            self.pos_blue_y = float(data[2])
            self.rotation_blue = float(data[3])
            self.pos_purple_x = float(data[4])
            self.pos_purple_y = float(data[5])
            self.rotation_purple = float(data[6])

        def getBlueData(self) -> tuple:
            """
            Return tuple with x, y and rotation
            """
            return tuple((self.pos_blue_x, self.pos_blue_y, self.rotation_blue))

        def getPurpleData(self) -> tuple:
            """
            Return tuple with x, y and rotation
            """
            return tuple((self.pos_purple_x, self.pos_purple_y, self.rotation_purple))

        def __str__(self) -> str:
            return ", ".join(
                [
                    self.timestamp.strftime(timestamp_format),
                    "(" + str(self.pos_blue_x),
                    str(self.pos_blue_y) + ")",
                    str(self.rotation_blue),
                    "(" + str(self.pos_purple_x),
                    str(self.pos_purple_y) + ")",
                    str(self.rotation_purple),
                ]
            )

    def positionList(self, getBlue: bool, position_list: list = None) -> list:
        result_list = []

        if position_list is None:
            position_list = self.pos_list

        if getBlue:
            for pos in position_list:
                result_list.append(pos.getBlueData())
        else:
            for pos in position_list:
                result_list.append(pos.getPurpleData())
        return result_list
    
    def getGamePos(self, start_time: datetime, end_time: datetime) -> list:
        return list(filter(lambda pos: pos.timestamp >= start_time and pos.timestamp <= end_time, self.pos_list))
    
class PlayerData:
    def __init__(self, player_data: str) -> None:
        self.event_list = []

        iterator = iter(player_data.splitlines())
        next(iterator)  # Skip first line
        for event_line in iterator:
            self.event_list.append(self.Event(event_line))

    class Event:
        def __init__(self, event: str) -> None:
            data = event.split(",")
            self.timestamp = datetime.strptime(data[0], timestamp_format)
            self.event_type = data[1]
            self.blue_balls_left = int(data[2])
            self.purple_balls_left = int(data[3])
            self.blue_lives = int(data[4])
            self.purple_lives = int(data[5])
            if len(data) > 6:
                self.corner = int(data[6])

        def isResetSceneEvent(self) -> bool:
            return self.event_type == "ResetScene" or self.event_type == "S"
        
        def isEndGameEvent(self) -> bool:
            return self.event_type == "GameEnd"
        
        def __str__(self) -> str:
            return f"Event({self.event_type}, {self.timestamp.strftime(timestamp_format)})"

    def numGames(self) -> int:
        return len(list(filter(lambda event: event.isResetSceneEvent(), self.event_list))) -2
    
    def getStartEndTimes(self, game_num: int = 0) -> tuple:
        """
        Get start and end times for a game.
        game_num=0 -> times for first game
        """
        if game_num > self.numGames():
            raise Exception(f"Number of games is {self.numGames()}, cannot get times for game number {game_num}")
        
        reset_scene_list = list(filter(lambda event: event.isResetSceneEvent(), self.event_list))[1::]
        end_game_list = list(filter(lambda event: event.isEndGameEvent(), self.event_list))

        # return reset_scene_list[game_num].timestamp, reset_scene_list[game_num+1].timestamp
        return reset_scene_list[game_num].timestamp, end_game_list[game_num].timestamp + timedelta(0, 0.2)
    
    def filterByEventType(self, type : str):
        return list(filter(lambda event : type in event.event_type, self.event_list))

class GameData:
    def __init__(self, date) -> None:
        self.pos_data = PositionData(getLogData("Position", date))
        self.player_data = PlayerData(getLogData("PlayerData", date))
        self.game_type = "RL" if self.pos_data.pos_list[0].pos_purple_y > -47 else "RuleBased"
        self.date = date
    
    def getEventPos(self, event_timestamp : datetime):
        closest_pos = None

        for pos in self.pos_data.pos_list:
            # check if new pos has a timestap closer to event_timestamp
            if closest_pos == None or (abs((event_timestamp-pos.timestamp).total_seconds()) < abs((event_timestamp-closest_pos.timestamp).total_seconds())):
                closest_pos = pos

        return closest_pos


    def __str__(self) -> str:
        return f"GameData({self.date}, type:{self.game_type}, num games:{self.player_data.numGames()})"

class GameDataContainer:
    def __init__(self, log_folders : list, unused_dates : list = []) -> None:
        # self.games = []

        files = []
        for folder in log_folders:
            files.extend(exploreFolder(folder))
        
        # dates = getUniqueDates(files)

        self.games = [GameData(date.strftime(date_format)) for date in getUniqueDates(files)]

        self.cleanGames(unused_dates)
        self.sortGames()

    def sortGames(self) -> None:
        self.games = sorted(self.games, key=lambda game_data : game_data.date)

    def cleanGames(self, unused_dates : list = []) -> None:
        self.games = list(filter(lambda game: game.player_data.numGames() > 0 and game.date not in unused_dates, self.games))

    def numGames(self) -> int:
        return len(self.games)

    def __str__(self) -> str:
        return f"GameDataContainer({[str(game) for game in self.games]})"