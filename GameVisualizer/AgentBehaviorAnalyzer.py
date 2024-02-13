import math

from GameVisualizer import PlayerData, PositionData, getLogData
from DataAnalyser import DataAnalyzer


MAPOCA_date = "2024-02-07_14-44-25"
FSM_date = "2024-02-07_14-50-44"
Imitation77M_date = "2024-02-07_14-57-05"
Reinforcement87M_date = "2024-02-07_15-02-52"
Reinforcement43M_date = "2024-02-08_15-04-58"
RewardShaping97M_date = "2024-02-08_14-48-22"
FSMNew_date = "2024-02-09_10-05-20"
FSMNewV2_date = "2024-02-09_14-02-04"
FSMNewV3_date = "2024-02-11_17-27-12"
NEAT_date = "2024-02-12_20-54-24"
FSM1_date = "2024-02-12_21-05-32"
FSM2_date = "2024-02-12_21-12-46"
FSM0_date = "2024-02-13_10-48-30"

y_delta = 34
margin = 0


def define_corners(y_delta=34, margin=0):
    return [(8.9 - margin, -20 + y_delta + margin), (34.9 + margin, -20 + y_delta + margin),
        (34.9 + margin, round(-73.9 + y_delta, 2) - margin), (8.9 - margin, round(-73.9 + y_delta, 2) - margin)]


def define_bushes(y_delta=34):
    bushes = [
        [(18.8, -64.5 + y_delta), (17.7, -64.5 + y_delta), (16.6, -64.5 + y_delta), (15.5, -64.5 + y_delta), (14.4, -64.5 + y_delta), (13.3, -64.5 + y_delta)],
        [(32.0, -64.5 + y_delta), (30.9, -64.5 + y_delta), (29.8, -64.5 + y_delta), (28.7, -64.5 + y_delta), (27.6, -64.5 + y_delta), (26.5, -64.5 + y_delta)],
        [(18.3, -54.6 + y_delta), (17.5, -55.4 + y_delta), (16.7, -56.2 + y_delta), (16.0, -57.0 + y_delta), (15.2, -57.8 + y_delta), (14.4, -58.5 + y_delta)],
        [(29.8, -58.5 + y_delta), (29.0, -57.8 + y_delta), (28.2, -57.0 + y_delta), (27.5, -56.2 + y_delta), (26.7, -55.4 + y_delta), (25.9, -54.6 + y_delta)],
        [(18.8, -42.8 + y_delta), (18.0, -42.0 + y_delta), (17.2, -41.2 + y_delta), (16.5, -40.5 + y_delta), (15.7, -39.7 + y_delta), (14.9, -38.9 + y_delta)],
        [(29.3, -38.9 + y_delta), (28.5, -39.7 + y_delta), (27.7, -40.5 + y_delta), (27.0, -41.2 + y_delta), (26.2, -42.0 + y_delta), (25.4, -42.8 + y_delta)],
        [(18.8, -31.9 + y_delta), (17.7, -31.9 + y_delta), (16.6, -31.9 + y_delta), (15.5, -31.9 + y_delta), (14.4, -31.9 + y_delta), (13.3, -31.9 + y_delta)],
        [(32.0, -31.7 + y_delta), (30.9, -31.7 + y_delta), (29.8, -31.7 + y_delta), (28.7, -31.7 + y_delta), (27.6, -31.7 + y_delta), (26.5, -31.7 + y_delta)],
    ]
    return bushes

corners = define_corners()
bushes = define_bushes()


def define_zones(corners, breadth_no=3, length_no=3):
    """
    Define the zones the court should be divided in. Assume that the court is not tilted.
    breadth_no is the number the breadth should be divided in.
    length_no is the number the length should be divided in.
    Return a dictionary with the coordinates of breadth_no * length_no zones.
    """
    dist_list = []
    for i in range(len(corners) - 1):
        for j in range(len(corners) - 1):
            if i != j:
                dist_list.append(math.dist(corners[i], corners[j]))
    
    # The breadth will be the shortest distance between corners in a rectangle
    breadth = min(dist_list)
    length = min(list(filter(lambda dist: dist != breadth, dist_list)))
    
    # Calculate breadth and length of each zone
    breadth = breadth / breadth_no
    length = length / length_no
    zone_dict = {}

    # Start defining the zones in the corner with the smallest coordinate values
    min_max_dict = get_min_and_max_for_rectangle(corners)
    start_corner = next((corner for corner in corners if corner[0] == min_max_dict["min_x"] and corner[1] == min_max_dict["min_y"]), None)

    for i in range(length_no):
        for j in range(breadth_no):
            coord_list = [start_corner, (start_corner[0]+breadth, start_corner[1]), (start_corner[0]+breadth, start_corner[1]+length), (start_corner[0], start_corner[1]+length)]
            zone_dict[(i,j)] = coord_list
            if j == breadth_no - 1 : start_corner = (start_corner[0]-(j*breadth), start_corner[1]+length)
            else : start_corner = (start_corner[0]+breadth, start_corner[1])
    
    return zone_dict


def get_min_and_max_for_rectangle(coordinates):
    """
    Return a dictionary with the min and max value for the x and y coordinates in a rectangle.
    Assume that the rectangle is not tilted.
    """
    x_coord = list(map(lambda corner: corner[0], coordinates))
    y_coord = list(map(lambda corner: corner[1], coordinates))
    coord_dict = {
        "min_x": min(x_coord),
        "max_x": max(x_coord),
        "min_y": min(y_coord),
        "max_y": max(y_coord),

    }
    return coord_dict


def define_hide_zone(distance=3):
    pass



class AgentBehaviorAnalyzer:

    def __init__(self, date="2024-02-07_14-44-25", fsm=False):
        self.date = date
        self.player_data = PlayerData(getLogData("PlayerData", date))
        self.position_data = PositionData(getLogData("Position", date))
        self.results_data = getLogData("Results", date)
        if fsm : self.zones = define_zones(define_corners(y_delta=0, margin=0.5), 1,2)
        else : self.zones = define_zones(define_corners(y_delta=34), 1,2)


    def find_closest_timestamp_in_positions(self, timestamp):
        """
        Return the timestamp in the position list that is closest to the given timestamp.
        """
        position_timestamps = list(map(lambda pos: pos.timestamp, self.position_data.pos_list))
        return min(position_timestamps, key=lambda t: abs(t - timestamp))
    

    def get_position_data(self, timestamp):
        """
        Return position data for a given timestamp.
        """
        closest = self.find_closest_timestamp_in_positions(timestamp=timestamp)
        return next((position for position in self.position_data.pos_list if position.timestamp == closest), None)


    def calculate_distance_between_agents(self, timestamp):
        """
        Calculate the distance between agents for a given timestamp.
        """
        pos_entry = self.get_position_data(timestamp)
        pos_blue = (pos_entry.pos_blue_x, pos_entry.pos_blue_y)
        pos_purple = (pos_entry.pos_purple_x, pos_entry.pos_purple_y)
        return math.dist(pos_blue, pos_purple)


    def calculate_average_throw_distance(self, agent="Blue"):
        """
        Calculate the average distance between the agent and the opponent when throwing the ball.
        """
        throw_list = list(filter(lambda event: (event.event_type == agent + "ThrewBall"), self.player_data.event_list))
        dist_list = []
        for throw in throw_list:
            dist_list.append(self.calculate_distance_between_agents(throw.timestamp))
        return sum(dist_list)/len(dist_list)
    

    def calculate_rotation_difference(self, timestamp, agent="Blue"):
        """
        Calculate how many degrees the agent is rotated relative to the opponent.
        A rotation difference of 0 means that the agent is looking directly at its opponent.
        A rotation difference of 180 means that the agent is facing the other way.
        """
        pos_entry = self.get_position_data(timestamp)
        angle_radians = math.atan2(pos_entry.pos_purple_y-pos_entry.pos_blue_y, pos_entry.pos_purple_x-pos_entry.pos_blue_x)
        angle_degrees = (math.degrees(angle_radians) - 90) % 360
        if agent == "Purple":
            angle_degrees = (180 - angle_degrees) % 360
            diff = pos_entry.rotation_purple - angle_degrees
        else:
            diff = pos_entry.rotation_blue - angle_degrees
        return abs((diff + 180) % 360 - 180)
    

    def calculate_average_throw_angle(self, agent="Blue"):
        """
        Calculate the average degree the agent is rotated relative to the opponent when throwing the ball.
        """
        throw_list = list(filter(lambda event: (event.event_type == agent + "ThrewBall"), self.player_data.event_list))
        angle_list = []
        for throw in throw_list:
            angle_list.append(self.calculate_rotation_difference(throw.timestamp, agent))
        return sum(angle_list)/len(angle_list)
    

    def calculate_angle_when_hit(self, agent="Blue", opponent_angle=True):
        """
        Calculate how many degrees the agent is rotated relative to the other when one of them is hit.
        agent denotes the agent that is hit.
        opponent_angle determines whether it is the opponent's angle that is calculated or the agent's angle.
        opponent_angle = True will typically give angles closer to 0 as the opponent is facing the agent when throwing.
        """
        hit_list = list(filter(lambda event: (event.event_type == "Hit" + agent), self.player_data.event_list))
        if opponent_angle:
            if agent == "Blue" : agent = "Purple"
            else : agent = "Blue"
        angle_list = []
        for hit in hit_list:
            angle_list.append(self.calculate_rotation_difference(hit.timestamp, agent))
        return angle_list
    

    def calculate_percentage_facing_opponent(self, agent="Blue", margin_degrees=10):
        """
        Calculate the fraction of time spent facing the opponent.
        margin_degrees is how many degrees agent can be rotated away from opponent while still being considered facing the opponent.
        """
        facing_list = list(filter(lambda pos: (self.calculate_rotation_difference(pos.timestamp, agent) < margin_degrees), self.position_data.pos_list))
        return len(facing_list)/len(self.position_data.pos_list)
    

    def find_agent_zone(self, timestamp, agent="Blue"):
        """
        Return the zone the agent is in for a given timestamp.
        """
        pos_entry = self.get_position_data(timestamp)
        pos = (pos_entry.pos_blue_x, pos_entry.pos_blue_y)
        if agent == "Purple" : pos = (pos_entry.pos_purple_x, pos_entry.pos_purple_y)

        for zone in self.zones.keys():
            min_max_dict = get_min_and_max_for_rectangle(self.zones[zone])
            is_in_x = pos[0] >= min_max_dict["min_x"] and pos[0] <= min_max_dict["max_x"]
            is_in_y = pos[1] >= min_max_dict["min_y"] and pos[1] <= min_max_dict["max_y"]
            if is_in_x and is_in_y:
                return zone
        return None
    

    def calculate_zone_percentage(self, agent="Blue"):
        """
        Return the percentage of time the agent spends in each zone.
        """
        zone_count = {}
        zone_percentage = {}
        for zone in self.zones.keys():
            zone_count[zone] = 0
        for pos in self.position_data.pos_list:
            zone = self.find_agent_zone(pos.timestamp, agent)
            zone_count[zone] += 1
        for zone in zone_count.keys():
            zone_percentage[zone] = zone_count[zone]/len(self.position_data.pos_list)
        return zone_percentage
    

    def find_start_zone(self, agent="Blue"):
        """
        Return the zone where the agent is in the beginning of the game
        """
        timestamp = self.position_data.pos_list[0].timestamp
        return self.find_agent_zone(timestamp, agent)
    

    def calculate_average_pickup_throw_time(self, agent="Blue"):
        """
        Calculate the how long it takes on average for the agent to throw the ball after pickup
        """
        pick_list = list(filter(lambda event: (event.event_type == agent + "PickedUpBall"), self.player_data.event_list))
        throw_list = list(filter(lambda event: (event.event_type == agent + "ThrewBall"), self.player_data.event_list))
        game_end_list = list(filter(lambda event: (event.event_type == "GameEnd"), self.player_data.event_list))
        reset_list = list(filter(lambda event: (event.event_type == "ResetScene"), self.player_data.event_list))
        time_list = []

        i = 0
        j = 0
        end_time = game_end_list[i].timestamp
        reset_time = reset_list[i+1].timestamp
        for throw in throw_list:
            throw_time = throw.timestamp
            pick_time = pick_list[j].timestamp
            # Don't include the throws that occur between games
            if throw_time > end_time and throw_time < reset_time:
                pass
            # Only want the time if pickup and throw occurred in the same game
            if throw_time > reset_time and i < len(reset_list):
                while pick_time < reset_time:
                    j += 1
                    pick_time = pick_list[j].timestamp
                i += 1
                if i < len(game_end_list):
                    end_time = game_end_list[i].timestamp
                    if i < len(reset_list) - 1 : reset_time = reset_list[i+1].timestamp
            j += 1
            time = throw_time - pick_time              
            time_list.append(time.total_seconds())
        return sum(time_list)/len(time_list)
    

    def calculate_rotation_change_percentage(self, agent="Blue"):
        """
        Calculate the percentage of the movements that are a rotation change in the opposite direction
        AI agents tend to have more jerky movements and thus a higher percentage
        """
        rot_change_count = 0
        right_turn = True
        if agent == "Blue" : prev_rot = self.position_data.pos_list[0].rotation_blue
        else : prev_rot = self.position_data.pos_list[0].rotation_purple
        for pos in self.position_data.pos_list[1:]:
            if agent == "Blue" : rot = pos.rotation_blue
            else : rot = pos.rotation_purple
            diff = ((rot - prev_rot) + 180) % 360 - 180
            prev_rot = rot
            is_turning_right = abs(diff) != diff
            if diff != 0 and (right_turn == is_turning_right):
                rot_change_count += 1
                right_turn = is_turning_right
        return rot_change_count/len(self.position_data.pos_list)
    

    def is_close_to_bush(self, timestamp, agent="Blue", distance=3):
        """
        Return True if agent is within a given distance from a bush for a given timestamp
        """
        pos_entry = self.get_position_data(timestamp)
        if agent == "Blue" : pos = (pos_entry.pos_blue_x, pos_entry.pos_blue_y)
        else : pos = (pos_entry.pos_purple_x, pos_entry.pos_purple_y)
        for bush in bushes:
            for bush_part in bush:
                if math.dist(pos, bush_part) < distance : return True
        return False
    

    def calculate_bush_closeness_percentage(self, agent="Blue", distance=3):
        """
        Calculate the percentage of time the agent spends within a given distance from a bush
        """
        close_list = list(filter(lambda pos: (self.is_close_to_bush(pos.timestamp, agent, distance)), self.position_data.pos_list))
        return len(close_list)/len(self.position_data.pos_list)
    

    def count_wins(self, agent="Blue"):
        """
        Count how many times the agent won a game
        """
        iterator = iter(self.results_data.splitlines())
        count = 0
        for result_line in iterator:
            data = result_line.split(",")
            if "Winner: " + agent in data[1]:
                count += 1
        return count
    

    def print_all_data(self):
        print("Average throw distance for Blue:", round(self.calculate_average_throw_distance("Blue"), 3))
        print("Average throw distance for Purple:", round(self.calculate_average_throw_distance("Purple"), 3))
        
        print()

        print("Average throw angle for Blue:", round(self.calculate_average_throw_angle("Blue"), 3))
        print("Average throw angle for Purple:", round(self.calculate_average_throw_angle("Purple"), 3))
        
        # print(ba.calculate_angle_when_hit("Purple"))
        # print(ba.calculate_angle_when_hit("Blue"))

        print()
        
        print("Percentage of time Blue faces opponent:", round(self.calculate_percentage_facing_opponent("Blue")*100, 3), "%")
        print("Percentage of time Purple faces opponent:", round(self.calculate_percentage_facing_opponent("Purple")*100, 3), "%")

        print()
        
        print("Blue starts in zone:", self.find_start_zone("Blue"))
        print("Percentage of time Blue spends in each zone:")
        for key in self.calculate_zone_percentage("Blue").keys():
            print(key, ":", round(self.calculate_zone_percentage("Blue")[key]*100, 3), "%")
        print()
        print("Purple starts in zone:", self.find_start_zone("Purple"))
        print("Percentage of time Purple spends in each zone:")
        for key in self.calculate_zone_percentage("Purple").keys():
            print(key, ":", round(self.calculate_zone_percentage("Purple")[key]*100, 3), "%")

        print()
        
        print("Average time from ball pickup to throw for Blue:", round(self.calculate_average_pickup_throw_time("Blue"), 3), "s")
        print("Average time from ball pickup to throw for Purple:", round(self.calculate_average_pickup_throw_time("Purple"), 3), "s")

        print()

        print("Percentage of time Blue changes rotation direction:", round(self.calculate_rotation_change_percentage("Blue")*100, 3), "%")
        print("Percentage of time Purple changes rotation direction:", round(self.calculate_rotation_change_percentage("Purple")*100, 3), "%")

        print()

        print("Percentage of time Blue is close to a bush:", round(self.calculate_bush_closeness_percentage("Blue", 3)*100, 3), "%")
        print("Percentage of time Purple is close to a bush:", round(self.calculate_bush_closeness_percentage("Purple")*100, 3), "%")



def compare(analyzers=[], da_analyzers=[], labels=[], agent="Purple"):
    spacing = 14
    extra_spacing = 6
    if agent == "Blue" : opponent = "Purple"
    else : opponent = "Blue"
    
    print(" ".ljust(spacing+extra_spacing), end="")
    for label in labels:
        print(label.ljust(spacing), end="")
    print("\n")

    print("No of games".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{a.count_wins(agent) + a.count_wins(opponent)}'.ljust(spacing), end="")
    print()

    print("No of wins".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{a.count_wins(agent)}'.ljust(spacing), end="")
    print()

    print("No of losses".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{a.count_wins(opponent)}'.ljust(spacing), end="")
    print()

    print("Win ratio".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        ratio = a.count_wins(agent) / (a.count_wins(agent) + a.count_wins(opponent))
        print(f'{round(ratio*100, 3)} %'.ljust(spacing), end="")
    print()

    print()

    print("No of pickups".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        print(f'{a.count_event_occurences(agent + "PickedUpBall")}'.ljust(spacing), end="")
    print()

    print("No of throws".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        print(f'{a.count_event_occurences(agent + "ThrewBall")}'.ljust(spacing), end="")
    print()

    print("No of hitting".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        print(f'{a.count_event_occurences("Hit" + opponent)}'.ljust(spacing), end="")
    print()

    print("No of being hit".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        print(f'{a.count_event_occurences("Hit" + agent)}'.ljust(spacing), end="")
    print()

    print()

    print("Hit ratio".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        ratio = a.count_event_occurences("Hit" + opponent)/(a.count_event_occurences("Hit" + agent) + a.count_event_occurences("Hit" + opponent))
        print(f'{round(ratio*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Precision".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        print(f'{round(a.calculate_precision(agent)*100, 2)} %'.ljust(spacing), end="")
    print()

    print("Faces opponent".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_percentage_facing_opponent(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Rotation change".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_rotation_change_percentage(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print()

    print("Avg ball hold".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        print(f'{round(a.calculate_average_ball_hold(agent), 3)}'.ljust(spacing), end="")
    print()

    print("Avg throw distance".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_average_throw_distance(agent), 3)}'.ljust(spacing), end="")
    print()

    print("Avg throw angle".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_average_throw_angle(agent), 3)}'.ljust(spacing), end="")
    print()

    print("Avg pickup time".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        print(f'{round(a.calculate_time_between_pickup(agent), 3)} s'.ljust(spacing), end="")
    print()

    print("Avg throw time".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_average_pickup_throw_time(agent), 3)} s'.ljust(spacing), end="")
    print()

    print()

    print("On blue side".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_zone_percentage(agent)[(1,0)]*100, 3)} %'.ljust(spacing), end="")
    print()

    print("On purple side".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_zone_percentage(agent)[(0,0)]*100, 3)} %'.ljust(spacing), end="")
    print()

    """ print("Close to bush".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_bush_closeness_percentage(agent, 3)*100, 3)} %'.ljust(spacing), end="")
    print() """


def find_closest_playstyle(analyzer, da_analyzer, analyzers=[], da_analyzers=[], agent="Blue"):
    """
    Compare statistics to find the agent with the most similar playstyle
    A score close to 0 indicates a similar playstyle
    """
    score_list = []
    for i in range(len(analyzers)):
        score = 0
        score += abs(analyzer.calculate_percentage_facing_opponent(agent) - analyzers[i].calculate_percentage_facing_opponent(agent))
        score += abs(analyzer.calculate_rotation_change_percentage(agent) - analyzers[i].calculate_rotation_change_percentage(agent))
        score += abs(analyzer.calculate_average_throw_distance(agent) - analyzers[i].calculate_average_throw_distance(agent)) / 10
        score += abs(analyzer.calculate_average_throw_angle(agent) - analyzers[i].calculate_average_throw_angle(agent)) / 10
        score += abs(analyzer.calculate_average_pickup_throw_time(agent) - analyzers[i].calculate_average_pickup_throw_time(agent)) / 10
        score += abs(da_analyzer.calculate_time_between_pickup(agent) - da_analyzers[i].calculate_time_between_pickup(agent)) / 10
        score += abs(da_analyzer.calculate_precision(agent) - da_analyzers[i].calculate_precision(agent))
        score_list.append(score)
    return score_list


def print_playstyle_table(dates={}, agent="Purple"):
    """
    Show an overview of each agent and how similar its playstyle is to each of the other agents' playstyles
    """
    analyzers = []
    da_analyzers = []
    for game in dates.keys():
        if "FSM" in game: analyzer = AgentBehaviorAnalyzer(dates[game], fsm=True)
        else : analyzer = AgentBehaviorAnalyzer(dates[game])
        da_analyzer = add_data_analyzer(dates[game])
        analyzers.append(analyzer)
        da_analyzers.append(da_analyzer)
    print_divider()
    spacing = 12
    extra_spacing = 4
    print(" ".ljust(spacing+extra_spacing), end="")
    for label in dates.keys():
        print(label.ljust(spacing), end="")
    print("\n")
    for i in range(len(analyzers)):
        score_list = find_closest_playstyle(analyzers[i], da_analyzers[i], analyzers, da_analyzers, agent)
        print(list(dates.keys())[i].ljust(spacing+extra_spacing), end="")
        for score in score_list:
            print(f'{round(score, 3)}'.ljust(spacing), end="")
        print()


def add_data_analyzer(date):
    da = DataAnalyzer()
    da.filename = "GameLog_Player_Data_" + date + ".txt"
    if ".meta" not in da.filename:
        da.read_data()
        da.clean_data()
        da.print_duration()
        da.save_data()
    return da


def print_divider():
    print()
    for i in range(120):
        print("=", end="")
    print("\n")


def compare_multiple_agents(dates={}, agent="Purple"):
    analyzers = []
    da_analyzers = []
    for game in dates.keys():
        if "FSM" in game: analyzer = AgentBehaviorAnalyzer(dates[game], fsm=True)
        else : analyzer = AgentBehaviorAnalyzer(dates[game])
        da_analyzer = add_data_analyzer(dates[game])
        analyzers.append(analyzer)
        da_analyzers.append(da_analyzer)
    print_divider()
    compare(analyzers, da_analyzers, dates.keys(), agent)


if __name__ == "__main__":
    print_divider()

    dates_pre_study = {
        "MA-POCA": MAPOCA_date,
        "IL" : Imitation77M_date,
        "RL-43M": Reinforcement43M_date,
        "RL-87M": Reinforcement87M_date,
        "RS": RewardShaping97M_date,
        "NEAT": NEAT_date,
        "FSM-V1": FSM1_date,
        "FSM-V2": FSM2_date,
        "FSM-V0": FSM0_date,
    }

    # compare_multiple_agents(dates_pre_study)

    dates_user1 = {
        "RL_1": "2024-02-11_20-52-26",
        "RL_2": "2024-02-11_20-45-12",
        "FSM_1": "2024-02-11_20-59-06",
        "FSM_2": "2024-02-11_20-38-07",
    }

    dates_user2 = {
        "RL_1": "2024-02-11_21-53-42",
        "RL_2": "2024-02-11_22-08-03",
        "FSM_1": "2024-02-11_21-58-33",
        "FSM_2": "2024-02-11_22-03-24",
    }

    dates_user3 = {
        "RL_1": "2024-02-11_21-53-42",
        "RL_2": "2024-02-12_13-36-25",
        "FSM_1": "2024-02-12_13-43-25",
        "FSM_2": "2024-02-12_13-50-32",
    }

    dates_user4 = {
        "RL_1": "2024-02-12_15-27-58",
        "RL_2": "2024-02-12_15-23-53",
        "FSM_1": "2024-02-12_15-32-41",
        "FSM_2": "2024-02-12_15-19-11",
    }


    

    print("USER 1")
    compare_multiple_agents(dates_user1, "Purple")
    print_divider()
    print("USER 2")
    compare_multiple_agents(dates_user2, "Purple")
    print_divider()
    print("USER 3")
    compare_multiple_agents(dates_user3, "Purple")
    print_divider()
    print("USER 4")
    compare_multiple_agents(dates_user4, "Purple")
    print_divider()



    # print_playstyle_table(dates_pre_study, agent="Purple")

    # fsm_new.calculate_average_pickup_throw_time(agent="Blue")
    

