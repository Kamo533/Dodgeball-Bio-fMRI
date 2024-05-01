import math
import pandas as pd
import csv

from LogInterpreter import PlayerData, PositionData, getLogData
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


def counter_clockwise(A, B, C):
    """
    Find out if three positions are in a counter clockwise direction.
    """
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
    

def lines_crossing(pos1, pos2, bush1, bush2):
    """
    Check if two lines are crossing, specifically the line between the agents and the line of the bush.
    """
    return counter_clockwise(pos1, bush1, bush2) != counter_clockwise(pos2, bush1, bush2) and counter_clockwise(pos1, pos2, bush1) != counter_clockwise(pos1, pos2, bush2)


def close_to_bush(pos, bush, distance=3):
    """
    Check if agent is located within a given distance from a bush.
    """
    for bush_part in bush:
        if math.dist(pos, bush_part) < distance : return True
    return False



class AgentBehaviorAnalyzer:

    def __init__(self, date="2024-02-07_14-44-25", subfolder="", fsm=False, split_in_two=False, first=True, game_no=None, split_no=None):
        """
        Initialize the analyzer with the date of the logs and the subfolder in which the logs are located.
        fsm is whether the game session took place in the fsm game environment.
        split_in_two is whether the game logs should be split in two in order to compare the first and second half.
        first is whether the first or the second half should be taken into consideration (if split_in_two is True).
        """
        self.date = date
        self.event_list = PlayerData(getLogData("PlayerData", date, subfolder)).event_list
        self.pos_list = PositionData(getLogData("Position", date, subfolder)).pos_list
        self.results_data = getLogData("Results", date, subfolder).splitlines()
        if fsm : y_delta = 0
        else : y_delta = 34
        self.zone_number_x = 3
        self.zone_number_y = 4
        self.zones = define_zones(define_corners(y_delta=y_delta, margin=0.5), self.zone_number_x, self.zone_number_y)
        self.bushes = define_bushes(y_delta=y_delta)
        self.da = add_data_analyzer(date, subfolder)
        # Split logs in two if split_in_two is True
        if split_in_two : self.split_logs_in_two(date, subfolder, first)
        elif split_no != None : self.split_logs(date, subfolder, nr=game_no, split_no=split_no)
        elif game_no != None : self.split_into_games(date, subfolder, game_no)
    

    def split_logs_in_two(self, date="2024-02-07_14-44-25", subfolder="", first=True):
        """
        Split all game logs in two for a specific game session.
        If first is True, the first half should be used, else, the second half should be used.
        """
        game_count = self.da.count_event_occurences("GameEnd")
        event_split_index = [i for i, n in enumerate(self.event_list) if n.event_type == "GameEnd"][game_count//2]
        timestamp = self.event_list[event_split_index].timestamp
        position = self.get_position_data(timestamp)
        pos_split_index = self.pos_list.index(position)
        if first:
            self.event_list = self.event_list[:event_split_index]
            self.pos_list = self.pos_list[:pos_split_index]
            self.results_data = self.results_data[:game_count//2]
            self.da = add_data_analyzer(date, subfolder, event_split_index, first)
        else:
            self.event_list = self.event_list[event_split_index:]
            self.pos_list = self.pos_list[pos_split_index:]
            self.results_data = self.results_data[game_count//2:]
            self.da = add_data_analyzer(date, subfolder, event_split_index, first)
    

    def split_logs_in_four(self, date="2024-02-07_14-44-25", subfolder="", nr=1):
        """
        Split all game logs in four for a specific game session.
        If first is True, the first half should be used, else, the second half should be used.
        """
        game_count = self.da.count_event_occurences("GameEnd")
        event_split_index = [i for i, n in enumerate(self.event_list) if n.event_type == "GameEnd"][game_count//4]
        timestamp = self.event_list[event_split_index].timestamp
        position = self.get_position_data(timestamp)
        pos_split_index = self.pos_list.index(position)
        if nr == 1:
            if nr == 1 : prev_event_index = 0
            else : prev_event_index = None
            self.event_list = self.event_list[nr-1:event_split_index]
            self.pos_list = self.pos_list[nr-1:pos_split_index]
            self.results_data = self.results_data[nr-1:game_count//4]
            self.da = add_data_analyzer(date, subfolder, event_split_index, False, prev_event_index)
        else:
            self.event_list = self.event_list[nr*event_split_index:]
            self.pos_list = self.pos_list[nr*pos_split_index:]
            self.results_data = self.results_data[nr*game_count//4:]
            self.da = add_data_analyzer(date, subfolder, event_split_index, False, prev_event_index)
    

    def split_into_games(self, date="2024-02-07_14-44-25", subfolder="", game_no=0):
        """
        Split all game logs so that only a single game is analyzed.
        game_no specifies which game that should be analyzed, in ascending order.
        """
        if game_no == 0:
            prev_event_index = 0
            prev_pos_index = 0
        else:
            prev_event_index = [i for i, n in enumerate(self.event_list) if n.event_type == "ResetScene"][game_no]
            prev_timestamp = self.event_list[prev_event_index].timestamp
            prev_position = self.get_position_data(prev_timestamp)
            prev_pos_index = self.pos_list.index(prev_position)

        event_index = [i for i, n in enumerate(self.event_list) if n.event_type == "ResetScene"][game_no+1]
        timestamp = self.event_list[event_index].timestamp
        position = self.get_position_data(timestamp)
        pos_index = self.pos_list.index(position)

        self.event_list = self.event_list[prev_event_index:event_index]
        self.pos_list = self.pos_list[prev_pos_index:pos_index]
        self.results_data = self.results_data[game_no:game_no+1]
        self.da = add_data_analyzer(date, subfolder, event_index, False, prev_event_index)

        # for event in self.event_list:
        #    print(event.event_type)
    

    def split_logs(self, date="2024-02-07_14-44-25", subfolder="", nr=0, split_no=4):
        game_count = self.da.count_event_occurences("ResetScene")
        event_index = [i for i, n in enumerate(self.event_list) if n.event_type == "ResetScene"][(nr+1)*game_count//split_no]
        timestamp = self.event_list[event_index].timestamp
        position = self.get_position_data(timestamp)
        pos_index = self.pos_list.index(position)
        
        if nr == 0:
            prev_event_index = 0
            prev_pos_index = 0
        else:
            prev_event_index = [i for i, n in enumerate(self.event_list) if n.event_type == "ResetScene"][nr*game_count//split_no]
            prev_timestamp = self.event_list[prev_event_index].timestamp
            prev_position = self.get_position_data(prev_timestamp)
            prev_pos_index = self.pos_list.index(prev_position)

        self.event_list = self.event_list[prev_event_index:event_index]
        self.pos_list = self.pos_list[prev_pos_index:pos_index]
        self.results_data = self.results_data[nr*game_count//split_no:(nr+1)*game_count//split_no]
        self.da = add_data_analyzer(date, subfolder, event_index, False, prev_event_index)


    def find_closest_timestamp_in_positions(self, timestamp):
        """
        Return the timestamp in the position list that is closest to the given timestamp.
        """
        position_timestamps = list(map(lambda pos: pos.timestamp, self.pos_list))
        return min(position_timestamps, key=lambda t: abs(t - timestamp))
    

    def get_position_data(self, timestamp):
        """
        Return position data for a given timestamp.
        """
        closest = self.find_closest_timestamp_in_positions(timestamp=timestamp)
        return next((position for position in self.pos_list if position.timestamp == closest), None)
    

    def get_position(self, pos_entry, agent="Blue"):
        if agent == "Blue" : pos = (pos_entry.pos_blue_x, pos_entry.pos_blue_y)
        else : pos = (pos_entry.pos_purple_x, pos_entry.pos_purple_y)
        return pos
    

    def get_opponent_position(self, pos_entry, agent="Blue"):
        if agent == "Blue" : pos = (pos_entry.pos_purple_x, pos_entry.pos_purple_y)
        else : pos = (pos_entry.pos_blue_x, pos_entry.pos_blue_y)
        return pos


    def calculate_distance_between_agents(self, timestamp):
        """
        Calculate the distance between agents for a given timestamp.
        """
        pos_entry = self.get_position_data(timestamp)
        pos_blue = (pos_entry.pos_blue_x, pos_entry.pos_blue_y)
        pos_purple = (pos_entry.pos_purple_x, pos_entry.pos_purple_y)
        return math.dist(pos_blue, pos_purple)
    

    def calculate_average_distance_between_agents(self):
        """
        Calculate the average distance between agents.
        """
        dist_sum = 0
        for pos_entry in self.pos_list:
            dist_sum += math.dist(self.get_position(pos_entry, "Blue"), self.get_position(pos_entry, "Purple"))
        return dist_sum/len(self.pos_list)


    def calculate_average_throw_distance(self, agent="Blue"):
        """
        Calculate the average distance between the agent and the opponent when throwing the ball.
        """
        throw_list = list(filter(lambda event: (event.event_type == agent + "ThrewBall"), self.event_list))
        dist_list = []
        for throw in throw_list:
            dist_list.append(self.calculate_distance_between_agents(throw.timestamp))
        if len(dist_list) == 0 : return -1
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
        throw_list = list(filter(lambda event: (event.event_type == agent + "ThrewBall"), self.event_list))
        angle_list = []
        for throw in throw_list:
            angle_list.append(self.calculate_rotation_difference(throw.timestamp, agent))
        if len(angle_list) == 0 : return -1
        return sum(angle_list)/len(angle_list)
    

    def calculate_angle_when_hit(self, agent="Blue", opponent_angle=True):
        """
        Calculate how many degrees the agent is rotated relative to the other when one of them is hit.
        agent denotes the agent that is hit.
        opponent_angle determines whether it is the opponent's angle that is calculated or the agent's angle.
        opponent_angle = True will typically give angles closer to 0 as the opponent is facing the agent when throwing.
        """
        hit_list = list(filter(lambda event: (event.event_type == "Hit" + agent), self.event_list))
        if opponent_angle:
            if agent == "Blue" : agent = "Purple"
            else : agent = "Blue"
        angle_list = []
        for hit in hit_list:
            angle_list.append(self.calculate_rotation_difference(hit.timestamp, agent))
        return angle_list
    

    def get_instances_of_facing_opponent(self, agent="Blue", margin_degrees=15):
        """
        Return a list of all position instances when the agent is facing its opponent
        """
        def is_facing(pos, agent, margin_degrees):
            return self.calculate_rotation_difference(pos.timestamp, agent) < margin_degrees
        
        def no_obstacles(pos, agent):
            pos_agent = self.get_position(pos, agent)
            pos_opp = self.get_opponent_position(pos, agent)
            for bush in self.bushes:
                bush_start, bush_end = bush[0], bush[-1]
                if lines_crossing(pos_agent, pos_opp, bush_start, bush_end) : return False
            return True

        return list(filter(lambda pos: is_facing(pos, agent, margin_degrees) and no_obstacles(pos, agent), self.pos_list))
    

    def calculate_percentage_facing_opponent(self, agent="Blue", margin_degrees=10):
        """
        Calculate the fraction of time spent facing the opponent.
        margin_degrees is how many degrees agent can be rotated away from opponent while still being considered facing the opponent.
        """
        facing_list = self.get_instances_of_facing_opponent(agent)
        return len(facing_list)/len(self.pos_list)
    

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
        for pos in self.pos_list:
            zone = self.find_agent_zone(pos.timestamp, agent)
            zone_count[zone] += 1
        for zone in zone_count.keys():
            zone_percentage[zone] = zone_count[zone]/len(self.pos_list)
        return zone_percentage
    

    def find_start_zone(self, agent="Blue"):
        """
        Return the zone where the agent is in the beginning of the game.
        """
        timestamp = self.pos_list[0].timestamp
        return self.find_agent_zone(timestamp, agent)
    

    def find_court_half_favor(self, agent="Blue"):
        """
        Return the percentage of time the agent spends in the same court half as it started in
        """
        zone_percentage = self.calculate_zone_percentage(agent)
        start_zone = self.find_start_zone(agent)
        half = self.zone_number_y // 2
        total_percentage = 0
        for zone in zone_percentage.keys():
            if start_zone[0] < half and zone[0] < half:
                total_percentage += zone_percentage[zone]
            elif self.zone_number_y % 2 == 0 and start_zone[0] >= half and zone[0] >= half:
                total_percentage += zone_percentage[zone]
            elif self.zone_number_y % 2 != 0 and start_zone[0] > half and zone[0] > half:
                total_percentage += zone_percentage[zone]
        return total_percentage


    def find_middle_court_favor(self, agent="Blue"):
        """
        Return the percentage of time the agent spends in the middle part of the court
        """
        zone_percentage = self.calculate_zone_percentage(agent)
        half = self.zone_number_x // 2
        total_percentage = 0
        for zone in zone_percentage.keys():
            if self.zone_number_x % 2 != 0 and zone[1] == half:
                total_percentage += zone_percentage[zone]
            elif self.zone_number_x % 2 == 0 and (zone[1] == half or zone[1] == half - 1):
                total_percentage += zone_percentage[zone]
        return total_percentage
    

    def calculate_average_pickup_throw_time(self, agent="Blue"):
        """
        Calculate the how long it takes on average for the agent to throw the ball after pickup.
        """
        pick_list = list(filter(lambda event: (event.event_type == agent + "PickedUpBall"), self.event_list))
        throw_list = list(filter(lambda event: (event.event_type == agent + "ThrewBall"), self.event_list))
        game_end_list = list(filter(lambda event: (event.event_type == "GameEnd"), self.event_list))
        reset_list = list(filter(lambda event: (event.event_type == "ResetScene"), self.event_list))
        time_list = []
        if len(game_end_list) < 1 : return -1
        if len(reset_list) < 2:
            reset_list = list(filter(lambda event: (event.event_type == "WinScreenStart"), self.event_list))
            reset_list.insert(0, None)
            if len(reset_list) < 2 : return -1

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
                    if len(pick_list) < j+1 : return -1000
                    pick_time = pick_list[j].timestamp
                i += 1
                if i < len(game_end_list):
                    end_time = game_end_list[i].timestamp
                    if i < len(reset_list) - 1 : reset_time = reset_list[i+1].timestamp
            j += 1
            time = throw_time - pick_time              
            time_list.append(time.total_seconds())
        if len(time_list) == 0 : return -1
        return sum(time_list)/len(time_list)
    

    def calculate_rotation_change_percentage(self, agent="Blue"):
        """
        Calculate the percentage of the movements that are a rotation change in the opposite direction.
        AI agents tend to have more jerky movements and thus a higher percentage.
        """
        rot_change_count = 0
        right_turn = True
        if agent == "Blue" : prev_rot = self.pos_list[0].rotation_blue
        else : prev_rot = self.pos_list[0].rotation_purple
        for pos in self.pos_list[1:]:
            if agent == "Blue" : rot = pos.rotation_blue
            else : rot = pos.rotation_purple
            diff = ((rot - prev_rot) + 180) % 360 - 180
            prev_rot = rot
            is_turning_right = abs(diff) != diff
            if diff != 0 and (right_turn == is_turning_right):
                rot_change_count += 1
                right_turn = is_turning_right
        return rot_change_count/len(self.pos_list)
    


    # NOT IN USE
    def is_close_to_bush(self, timestamp, agent="Blue", distance=3):
        """
        Return True if agent is within a given distance from a bush for a given timestamp.
        """
        pos_entry = self.get_position_data(timestamp)
        pos = self.get_position(pos_entry, agent)
        for bush in bushes:
            for bush_part in bush:
                if math.dist(pos, bush_part) < distance : return True
        return False
    

    # NOT IN USE
    def calculate_bush_closeness_percentage(self, agent="Blue", distance=3):
        """
        Calculate the percentage of time the agent spends within a given distance from a bush.
        """
        close_list = list(filter(lambda pos: (self.is_close_to_bush(pos.timestamp, agent, distance)), self.pos_list))
        return len(close_list)/len(self.pos_list)



    def calculate_hiding_percentage(self, agent="Blue"):
        """
        Calculate the percentage of time the agent spends hiding from the opponent behind a bush.
        """
        hiding_count = 0
        for pos_entry in self.pos_list:
            pos = self.get_position(pos_entry, agent)
            pos_opponent = self.get_opponent_position(pos_entry, agent)
            for bush in self.bushes:
                bush_start, bush_end = bush[0], bush[-1]
                # Is hiding if the line between the agents is crossing the bush and the agent is close to that bush
                if lines_crossing(pos, pos_opponent, bush_start, bush_end) and close_to_bush(pos, bush):
                    hiding_count += 1
        return hiding_count/len(self.pos_list)

    

    def count_wins(self, agent="Blue"):
        """
        Count how many times the agent won a game.
        """
        if self.count_games() < 2:
            opponent = "Purple"
            if agent == "Purple" : opponent = "Blue"
            if self.da.count_event_occurences("Hit" + opponent) == 3:
                return 1
        iterator = iter(self.results_data)
        count = 0
        for result_line in iterator:
            data = result_line.split(",")
            if "Winner: " + agent in data[1]:
                count += 1
        return count
        

    def count_games(self):
        """
        Count the number of games in the game log.
        """
        return self.da.count_event_occurences("ResetScene")
    

    def get_result(self):
        """ Get result from a single game or from the entire game session """
        return str(self.count_wins("Blue")) + "-" + str(self.count_wins("Purple"))
    

    def count_move(self, agent="Blue", pos_list=[], move_away=True):
        """
        Count how many time intervals the agent moves away from or moves towards its opponent.
        """
        move_count = 0
        prev_pos_entry = pos_list[0]
        prev_distance = self.calculate_distance_between_agents(prev_pos_entry.timestamp)
        prev_opponent_pos = self.get_opponent_position(prev_pos_entry, agent)
        for pos_entry in pos_list[1:]:
            pos = self.get_position(pos_entry, agent)
            new_distance = math.dist(pos, prev_opponent_pos)
            if move_away:
                if new_distance > prev_distance:
                    move_count += 1
            else:
                if new_distance < prev_distance:
                    move_count += 1
            prev_distance = self.calculate_distance_between_agents(pos_entry.timestamp)
            prev_opponent_pos = self.get_opponent_position(pos_entry, agent)
        return move_count

    
    def find_move_away_percentage(self, agent="Blue"):
        """
        Calculate the percentage of time the agent spends moving away from its opponent.
        """
        move_away_count = self.count_move(agent, self.pos_list)
        return move_away_count/len(self.pos_list)
    

    def find_move_towards_percentage(self, agent="Blue"):
        """
        Calculate the percentage of time the agent spends moving away from its opponent.
        """
        move_away_count = self.count_move(agent, self.pos_list, move_away=False)
        return move_away_count/len(self.pos_list)
    

    def calculate_move_when_facing_opponent(self, agent="Blue", margin_degrees=20, move_away=True):
        """
        Calculate the percentage of time the agent spends moving away from or moving towards its opponent when it sees the opponent.
        """
        facing_list = self.get_instances_of_facing_opponent(agent, margin_degrees)
        move_count = 0
        if len(facing_list) > 1 : prev_pos_entry = facing_list[0]
        else : return -1
        sub_facing_list = []
        for pos_entry in facing_list:
            if pos_entry.timestamp - prev_pos_entry.timestamp < pd.Timedelta(seconds=1):
                sub_facing_list.append(pos_entry)
            elif len(sub_facing_list) > 1:
                move_count += self.count_move(agent, sub_facing_list, move_away=move_away)
                sub_facing_list = []
            else:
                sub_facing_list = []
            prev_pos_entry = pos_entry
        return move_count/len(facing_list)



    def print_all_data(self):
        print("Average throw distance for Blue:", round(self.calculate_average_throw_distance("Blue"), 3))
        print("Average throw distance for Purple:", round(self.calculate_average_throw_distance("Purple"), 3))
        print()
        print("Average throw angle for Blue:", round(self.calculate_average_throw_angle("Blue"), 3))
        print("Average throw angle for Purple:", round(self.calculate_average_throw_angle("Purple"), 3))
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
        print(f'{round(a.calculate_precision(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Faces opponent".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_percentage_facing_opponent(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Rotation change".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_rotation_change_percentage(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Moves away".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.find_move_away_percentage(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Moves towards".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.find_move_towards_percentage(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Moves away facing".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_move_when_facing_opponent(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Moves towards facing".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_move_when_facing_opponent(agent, move_away=False)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Is hiding".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_hiding_percentage(agent)*100, 3)} %'.ljust(spacing), end="")
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

    print("Avg agent distance".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_average_distance_between_agents(), 3)}'.ljust(spacing), end="")
    print()

    print("Avg game length".ljust(spacing+extra_spacing), end="")
    for a in da_analyzers:
        print(f'{round(a.get_average_game_length(), 3)} s'.ljust(spacing), end="")
    print()

    print()

    print("Court half favor".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.find_court_half_favor(agent)*100, 3)} %'.ljust(spacing), end="")
    print()

    print("Middle court favor".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.find_middle_court_favor(agent)*100, 3)} %'.ljust(spacing), end="")
    print()



def generate_statistics_dict(date_list=[{}], subfolder="", player="", split_in_two=False, start_id=1, split_in_games=False, split_no=None):
    """
    Return a list of fields (measures) for the csv file, as well as a dictionary with all statistics.
    If no player is specified, data for both players are returned.
    If split_in_two is True, each game log will be split in two.
    """
    statistics_dict = []
    labels = list(date_list[0].keys())

    def add_statistics(user_dict={}, agent="Purple", agent_marker="", labels=[]):
        """
        Add all statistics to the user dictionary.
        """
        if agent == "Blue" : opponent = "Purple"
        else : opponent = "Blue"

        j = 0
        for a in analyzers:
            win_ratio = -1
            if a.count_wins(agent) + a.count_wins(opponent) != 0:
                win_ratio = a.count_wins(agent) / (a.count_wins(agent) + a.count_wins(opponent))
            print(labels[j] + agent_marker)
            print("Number of games:", a.count_games())
            print("Blue wins:", a.count_wins("Blue"))
            print("Purple wins:", a.count_wins("Purple"))
            print()
            user_dict["Win ratio " + labels[j] + agent_marker] = round(win_ratio*100, 3)
            user_dict["Opponent observation " + labels[j] + agent_marker] = round(a.calculate_percentage_facing_opponent(agent)*100, 3)
            user_dict["Rotation change " + labels[j] + agent_marker] = round(a.calculate_rotation_change_percentage(agent)*100, 3)
            user_dict["Approach " + labels[j] + agent_marker] = round(a.find_move_towards_percentage(agent)*100, 3)
            user_dict["Retreat " + labels[j] + agent_marker] = round(a.find_move_away_percentage(agent)*100, 3)
            user_dict["Aggressive movements " + labels[j] + agent_marker] = round(a.calculate_move_when_facing_opponent(agent, move_away=False)*100, 3)
            user_dict["Defensive movements " + labels[j] + agent_marker] = round(a.calculate_move_when_facing_opponent(agent)*100, 3)
            user_dict["Hiding " + labels[j] + agent_marker] = round(a.calculate_hiding_percentage(agent)*100, 3)
            user_dict["Throw distance " + labels[j] + agent_marker] = round(a.calculate_average_throw_distance(agent), 3)
            user_dict["Throw angle " + labels[j] + agent_marker] = round(a.calculate_average_throw_angle(agent), 3)
            user_dict["Throw time " + labels[j] + agent_marker] = round(a.calculate_average_pickup_throw_time(agent), 3)
            user_dict["Court half favor " + labels[j] + agent_marker] = round(a.find_court_half_favor(agent)*100, 3)
            user_dict["Middle court favor " + labels[j] + agent_marker] = round(a.find_middle_court_favor(agent)*100, 3)
            user_dict["Agent distance " + labels[j]] = round(a.calculate_average_distance_between_agents(), 3)
            user_dict["Number of games " + labels[j]] = a.count_games()
            user_dict["Result " + labels[j]] = a.get_result()
            j += 1
        
        j = 0
        for a in da_analyzers:
            hit_ratio = a.count_event_occurences("Hit" + opponent)/(a.count_event_occurences("Hit" + agent) + a.count_event_occurences("Hit" + opponent))
            user_dict["Hit ratio " + labels[j] + agent_marker] = round(hit_ratio*100, 3)
            user_dict["Precision " + labels[j] + agent_marker] = round(a.calculate_precision(agent)*100, 3)
            user_dict["Ball hold " + labels[j] + agent_marker] = round(a.calculate_average_ball_hold(agent), 3)
            user_dict["Pick-up time " + labels[j] + agent_marker] = round(a.calculate_time_between_pickup(agent), 3)
            user_dict["Game duration " + labels[j]] = round(a.get_average_game_length(), 3)
            j += 1
        
        return user_dict
    
    def generate_fields(measure="", fields=[]):
        """
        Add fields that should be present in the csv file.
        """
        for agent in labels:
            if player == "Blue" : fields.append(measure + " " + agent + " (user)")
            else : fields.append(measure + " " + agent + " (agent)")
        if player == "":
            for agent in labels:
                fields.append(measure + " " + agent + " (user)")
        return fields
    
    i = start_id
    changed = False
    for dates in date_list:
        # If subfolder is None, the logs are in different subfolders
        if subfolder == None or changed:
            subfolder = "/fMRI_" + next(iter(dates.values()))[:10]
            changed = True
        all_analyzers, all_da_analyzers, game_count = prepare_comparison(dates, subfolder, split_in_two, split_in_games, split_no)
        
        n = 1
        if split_in_two : n = 2
        if game_count != None : n = game_count
        if split_no != None : n = split_no
        for j in range(n):
            user_dict = {}
            # FIRST you get all for FSM, THEN for RL (or opposite)
            # analyzers [FSM 1. half, FSM 2. half, RL 1. half, RL 2. half]
            # analyzers [FSM 1. half, FSM 2. half, RL 1. half, RL 2. half, XX 1. half, XX 2. half]
            # if j == 0 : analyzers, da_analyzers = all_analyzers[::n], all_da_analyzers[::n]      # all_analyzers[:len(labels)], all_da_analyzers[:len(labels)]
            # else : analyzers, da_analyzers = all_analyzers[j::n], all_da_analyzers[j::n]       # all_analyzers[len(labels):], all_da_analyzers[len(labels):]
            analyzers, da_analyzers = all_analyzers[j::n], all_da_analyzers[j::n]
            user_dict["User"] = i
            print("ID:", i)
            if player == "Blue" : add_statistics(user_dict, player, " (user)", labels)
            else : add_statistics(user_dict, "Purple", " (agent)", labels)
            if player == "":
                add_statistics(user_dict, "Blue", " (user)", labels)
            statistics_dict.append(user_dict)
            if split_in_two or game_count != None or split_no != None : i += 1/n
            else : i += 1
    
    fields = ["User"]
    generate_fields("Win ratio", fields)
    generate_fields("Hit ratio", fields)
    generate_fields("Precision", fields)
    generate_fields("Pick-up time", fields)
    generate_fields("Throw time", fields)
    generate_fields("Ball hold", fields)
    generate_fields("Throw distance", fields)
    generate_fields("Throw angle", fields)
    generate_fields("Rotation change", fields)
    generate_fields("Opponent observation", fields)
    generate_fields("Approach", fields)
    generate_fields("Retreat", fields)
    generate_fields("Aggressive movements", fields)
    generate_fields("Defensive movements", fields)
    generate_fields("Hiding", fields)
    generate_fields("Court half favor", fields)
    generate_fields("Middle court favor", fields)
    for agent in labels:
        fields.append("Agent distance " + agent)
    for agent in labels:
        fields.append("Game duration " + agent)
    for agent in labels:
        fields.append("Number of games " + agent)
    for agent in labels:
        fields.append("Result " + agent)

    return fields, statistics_dict


def write_to_csv(filename, fields, statistics_dict):
    """
    Write the data from the statistics dictionary to a csv file.
    """
    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        writer.writerows(statistics_dict)


def create_csv_file(filename, date_list=[{}], subfolder="", player="", split_in_two=False, start_id=1, split_in_games=False, split_no=None):
    """
    Create a csv file with a given filename in a given subfolder for a given list of game sessions.
    If subfolder is None, the logs are in different subfolders that should be identified based on their names.
    If split_in_two is True, each log will be split in two so that the two halves can be compared.
    """
    fields, statistics_dict = generate_statistics_dict(date_list, subfolder, player, split_in_two, start_id, split_in_games, split_no)
    write_to_csv(filename, fields, statistics_dict)


# NOT IN USE
def find_closest_playstyle(analyzer, da_analyzer, analyzers=[], da_analyzers=[], agent="Blue"):
    """
    Compare statistics to find the agent with the most similar playstyle.
    A score close to 0 indicates a similar playstyle.
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


# NOT IN USE
def print_playstyle_table(dates={}, agent="Purple", subfolder=""):
    """
    Show an overview of each agent and how similar its playstyle is to each of the other agents' playstyles.
    """
    analyzers = []
    da_analyzers = []
    for game in dates.keys():
        if "FSM" in game: analyzer = AgentBehaviorAnalyzer(dates[game], fsm=True, subfolder=subfolder)
        else : analyzer = AgentBehaviorAnalyzer(dates[game], subfolder=subfolder)
        da_analyzer = add_data_analyzer(dates[game], subfolder=subfolder)
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


def add_data_analyzer(date, subfolder="", split_index=None, first=True, prev_split_index=None):
    """
    Create a data analyzer object based on the date and the subfolder.
    split_index should be different from None if only part of the log should be analyzed.
    """
    if split_index == None:
        da = DataAnalyzer(subfolder)
    elif prev_split_index != None:
        da = DataAnalyzer(subfolder, prev_split_index, split_index)
    else:
        if first : da = DataAnalyzer(subfolder, None, split_index)
        else : da = DataAnalyzer(subfolder, split_index, None)
    da.filename = "GameLog_Player_Data_" + date + ".txt"
    if ".meta" not in da.filename:
        da.read_data()
        da.clean_data()
        da.print_duration()
        da.save_data()
    return da


def print_divider():
    """
    Divide the data nicely when printing to terminal.
    """
    print()
    for i in range(120):
        print("=", end="")
    print("\n")


def prepare_comparison(dates={}, subfolder="", split_in_two=False, split_in_games=False, split_no=None):
    """
    Return analyzers and da_analyzers associated with a specific dates dictionary (usually for one specific player).
    If split_in_two is True, each log is split in two.
    The function will thus return two analyzers and two da_analyzers per game session (date).
    """
    analyzers = []
    da_analyzers = []
    game_count = None

    # Analyze the same amount of games for both agents
    if split_in_games:
        for game in dates.keys():
            fsm = False
            if "fsm" in game.lower() : fsm = True
            analyzer = AgentBehaviorAnalyzer(dates[game], subfolder, fsm=fsm, split_in_two=split_in_two, first=True)
            games = analyzer.count_games()
            if game_count == None or game_count > games : game_count = games
    
    for game in dates.keys():
        fsm = False
        if "fsm" in game.lower() : fsm = True
        analyzer = AgentBehaviorAnalyzer(dates[game], subfolder, fsm=fsm, split_in_two=split_in_two, first=True)

        # If we should split the game log into individual games
        if split_in_games:
            for i in range(game_count):
                analyzer = AgentBehaviorAnalyzer(dates[game], subfolder, fsm=fsm, split_in_two=split_in_two, first=True, game_no=i)
                analyzers.append(analyzer)
                da_analyzers.append(analyzer.da)
        
        if split_no != None:
            for i in range(split_no):
                analyzer = AgentBehaviorAnalyzer(dates[game], subfolder, fsm=fsm, split_in_two=split_in_two, first=False, game_no=i, split_no=split_no)
                analyzers.append(analyzer)
                da_analyzers.append(analyzer.da)
        
        # If we should analyze the whole game log or split it in two
        else:
            analyzers.append(analyzer)
            da_analyzers.append(analyzer.da)
            if split_in_two:
                analyzer_2 = AgentBehaviorAnalyzer(dates[game], subfolder, fsm=fsm, split_in_two=True, first=False)
                analyzers.append(analyzer_2)
                da_analyzers.append(analyzer_2.da)

    return analyzers, da_analyzers, game_count


def compare_multiple_agents(dates={}, agent="Purple", subfolder=""):
    """
    Print statistics for each item (game session) in the date dictionary.
    """
    analyzers, da_analyzers, game_count = prepare_comparison(dates, subfolder)
    print_divider()
    print("Game count:", game_count)
    compare(analyzers, da_analyzers, dates.keys(), agent)


def show_study_results(date_list=[{}], agent="Purple", subfolder=""):
    """
    Print statistics for multiple users at the same time.
    The dictionaries in date_list each contain the dates of the game sessions for a single user.
    """
    i = 1
    for dates in date_list:
        print_divider()
        print("USER", i, "---", agent)
        print_divider()
        compare_multiple_agents(dates, agent, subfolder)
        i += 1



if __name__ == "__main__":

    # ============================= Pre study =================================

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

    dates_tournament = {
        "RL-FSM": "2024-04-14_16-25-51",
        "IL-FSM": "2024-04-14_16-36-35"
    }

    # show_study_results([dates_pre_study], "Purple", "/PreStudy")
    # print_playstyle_table(dates_pre_study, "Purple", "/PreStudy")
    # create_csv_file("pre_study.csv", [dates_pre_study], "/PreStudy", "Purple")
    # show_study_results([dates_tournament], "Blue", "/FSM-RL")
    # show_study_results([dates_tournament], "Purple", "/FSM-RL")

    # ========================================================================


    # ============================ Pilot study ===============================

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
        "RL_1": "2024-02-12_13-57-56",
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
    dates_pilot = [dates_user1, dates_user2, dates_user3, dates_user4]
    # show_study_results(dates_pilot, "Purple", "/PilotStudy")
    # create_csv_file("pilot_study.csv", dates_pilot, "/PilotStudy", both_players=False)

    # ==========================================================================


    # ======================= (Pilot) Experiments ==============================

    dates_fmri_1 = {
        "RL": "2024-02-13_19-05-14",
        "FSM": "2024-02-13_19-19-16"
    }
    dates_fmri_2 = {
        "RL": "2024-02-13_20-36-09",
        "FSM": "2024-02-13_20-22-08"
    }
    # show_study_results([dates_fmri_1, dates_fmri_2], "Purple", "/fMRI")
    # show_study_results([dates_fmri_1, dates_fmri_2], "Blue", "/fMRI")
    # create_csv_file("pilot_fmri.csv", [dates_fmri_1, dates_fmri_2], "/fMRI", both_players=False)

    # ======================================================================


    # ======================= Post pilot experiments =======================

    dates_post_fmri = {
        "FSM": "2024-02-14_16-35-48",
        "RL": "2024-02-14_16-43-48"
    }
    dates_fsm4 = {
        "FSM 4.1": "2024-02-20_14-47-23",
        "FSM 4.2": "2024-02-20_15-19-53",
        "RL": "2024-02-20_14-35-25"
    }
    # show_study_results([dates_post_fmri], "Purple", "/Analyze")
    # show_study_results([dates_fsm4], "Purple", "/Analyze/FSM-4")

    # ========================================================================



    # ======================= Test different parameters =======================

    fsm_rl_five_balls = {
        "FSM 4": "2024-02-25_13-55-29",
        "FSM 5": "2024-02-25_14-10-21"
    }
    fsm_rl_four_balls = {
        "FSM 4": "2024-02-25_21-10-02",
        "FSM 5": "2024-02-25_21-21-02"
    }
    five_balls = {
        "FSM 4": "2024-02-25_21-49-40",
        "FSM 5": "2024-02-25_21-57-06",
        "RL": "2024-02-25_22-04-26"
    }
    four_balls = {
        "FSM 4": "2024-02-25_22-13-32",
        "FSM 5": "2024-02-25_22-28-52",
        "RL": "2024-02-25_22-20-20"
    }
    # show_study_results([fsm_rl_five_balls], "Blue", "/FSM-RL")
    # show_study_results([fsm_rl_five_balls], "Purple", "/FSM-RL")
    # show_study_results([fsm_rl_four_balls], "Blue", "/FSM-RL")
    # show_study_results([fsm_rl_four_balls], "Purple", "/FSM-RL")
    # show_study_results([five_balls], "Purple", "/Analyze/FSM-4")
    # show_study_results([four_balls], "Purple", "/Analyze/FSM-4")

    # ======================================================================



    # ======================= Compare agents ===============================

    compare_fsm_0 = {
        "FSM 4": "2024-02-26_10-51-49",
        "FSM 5": "2024-02-26_11-24-28",
        "RL": "2024-02-26_10-40-19"
    }
    # show_study_results([compare_fsm_0], "Purple", "/Analyze/FSM-4")

    fsm_rl_4_55 = {
        "5.5 throw chance": "2024-02-26_13-15-44",
    }
    fsm_rl_4_7 = {
        "fsm-rl 7.0 throw chance": "2024-02-26_14-44-42"
    }

    # show_study_results([fsm_rl_4_7], "Blue", "/FSM-RL")
    # show_study_results([fsm_rl_4_7], "Purple", "/FSM-RL")
    # create_csv_file("comparison.csv", [fsm_rl_4_7], "/FSM-RL")

    # ======================================================================
    
    
    # ============================ Div testing =============================
    
    # Not accessible
    dates_pre_fmri = {
        "FSM": "2024-02-13_15-57-30",
        "RL": "2024-02-13_16-02-46"
    }
    elen = {
        "FSM": "2024-02-26_12-01-15",
        "RL": "2024-02-26_12-07-26"
    }
    sindre = {
        "FSM": "2024-02-26_12-20-53",
        "RL": "2024-02-26_12-15-05"
    }
    # show_study_results([elen, sindre], "Purple", "/ElenTest")
    # show_study_results([elen, sindre], "Blue", "/ElenTest")

    dates_comparison = {
        "FSM-RL": "2024-02-23_12-30-10",
        "FSM-RL 2": "2024-02-23_12-48-03",
    }
    test_comparison = {
        "RL-RL": "2024-02-25_12-49-26",
    }
    fsm0_rl = {
        "FSM0-RL": "2024-02-25_13-13-26"
    }
    # show_study_results([dates_comparison], "Blue", "/FSM-RL")
    # show_study_results([test_comparison], "Purple", "/FSM-RL")
    # show_study_results([fsm0_rl], "Blue", "/FSM-RL")
    # show_study_results([fsm0_rl], "Purple", "/FSM-RL")

    # ======================================================================


    # ============================== Experiments ==============================

    dates_id_18 = {
        "FSM": "2024-02-27_14-29-02",
        "RL": "2024-02-27_14-13-36"
    }
    dates_id_19 = {
        "FSM": "2024-02-27_18-36-02",
        "RL": "2024-02-27_18-53-21"
    }
    dates_id_20 = {
        "FSM": "2024-02-27_20-10-18",
        "RL": "2024-02-27_19-47-30"
    }
    dates_id_21 = {
        "FSM": "2024-03-05_13-20-16",
        "RL": "2024-03-05_13-41-09"
    }
    dates_id_22 = {
        "FSM": "2024-03-05_15-04-18",
        "RL": "2024-03-05_14-36-32"
    }
    dates_id_23 = {
        "FSM": "2024-03-05_18-28-50",
        "RL": "2024-03-05_18-55-57"
    }
    dates_id_24 = {
        "FSM": "2024-03-05_20-12-41",
        "RL": "2024-03-05_19-46-27"
    }
    dates_id_25 = {
        "FSM": "2024-03-12_13-10-38",
        "RL": "2024-03-12_13-36-57"
    }
    dates_id_26 = {
        "FSM": "2024-03-12_16-31-30",
        "RL": "2024-03-12_16-04-04"
    }
    dates_id_27 = {
        "FSM": "2024-03-12_18-27-58",
        "RL": "2024-03-12_18-54-45"
    }
    dates_id_28 = {
        "FSM": "2024-03-12_20-21-31",
        "RL": "2024-03-12_19-58-37"
    }
    dates_id_29 = {
        "FSM": "2024-03-14_12-18-39",
        "RL": "2024-03-14_12-42-37"
    }
    dates_id_30 = {
        "FSM": "2024-03-14_14-00-53",
        "RL": "2024-03-14_13-35-23"
    }
    dates_id_31 = {
        "FSM": "2024-03-19_13-30-40",
        "RL": "2024-03-19_13-54-06"
    }
    dates_id_32 = {
        "FSM": "2024-03-21_10-35-53",
        "RL": "2024-03-21_10-10-30"
    }
    dates_id_33 = {
        "FSM": "2024-03-21_11-59-36",
        "RL": "2024-03-21_12-27-06"
    }
    dates_id_34 = {
        "FSM": "2024-03-21_13-55-00",
        "RL": "2024-03-21_13-28-38"
    }


    dates_2702 = [dates_id_18, dates_id_19, dates_id_20]
    dates_0503 = [dates_id_21, dates_id_22, dates_id_23, dates_id_24]
    dates_1203 = [dates_id_25, dates_id_26, dates_id_27, dates_id_28]
    dates_1403 = [dates_id_29, dates_id_30]
    dates_1903 = [dates_id_31]
    dates_2103 = [dates_id_32, dates_id_33, dates_id_34]
    dates = [dates_id_18, dates_id_19, dates_id_20, dates_id_21, dates_id_22, dates_id_23, dates_id_24, 
        dates_id_25, dates_id_26, dates_id_27, dates_id_28, dates_id_29, dates_id_30, dates_id_31,
        dates_id_32, dates_id_33, dates_id_34]

    # create_csv_file("fMRI-2702-split.csv", dates_2702, None, player="Blue", split_in_two=True, start_id=18)
    # create_csv_file("fMRI-0503-split.csv", dates_0503, None, player="Blue", split_in_two=True, start_id=21)
    # create_csv_file("fMRI-1203-split.csv", dates_1203, None, player="Blue", split_in_two=True, start_id=25)
    # create_csv_file("fMRI-1403-split.csv", dates_1403, None, player="Blue", split_in_two=True, start_id=29)
    # create_csv_file("fMRI-1903-split.csv", dates_1903, None, player="Blue", split_in_two=True, start_id=31)
    # create_csv_file("fMRI-2103-split.csv", dates_2103, None, player="Blue", split_in_two=True, start_id=32)

    # create_csv_file("fMRI-2702-agents.csv", dates_2702, None, player="", split_in_two=False, start_id=18)
    # create_csv_file("fMRI-0503-agents.csv", dates_0503, None, player="", split_in_two=False, start_id=21)
    # create_csv_file("fMRI-1203-agents.csv", dates_1203, None, player="", split_in_two=False, start_id=25)
    # create_csv_file("fMRI-1403-agents.csv", dates_1403, None, player="", split_in_two=False, start_id=29)
    # create_csv_file("fMRI-1903-agents.csv", dates_1903, None, player="", split_in_two=False, start_id=31)
    # create_csv_file("fMRI-2103-agents.csv", dates_2103, None, player="", split_in_two=False, start_id=32)

    # create_csv_file("fMRI-2702-games.csv", dates_2702, None, player="Blue", split_in_two=False, start_id=18, split_in_games=True)
    # create_csv_file("fMRI-0503-games.csv", dates_0503, None, player="Blue", split_in_two=False, start_id=21, split_in_games=True)
    # create_csv_file("fMRI-1203-games.csv", dates_1203, None, player="Blue", split_in_two=False, start_id=25, split_in_games=True)
    # create_csv_file("fMRI-1403-games.csv", dates_1403, None, player="Blue", split_in_two=False, start_id=29, split_in_games=True)
    # create_csv_file("fMRI-1903-games.csv", dates_1903, None, player="Blue", split_in_two=False, start_id=31, split_in_games=True)
    # create_csv_file("fMRI-2103-games.csv", dates_2103, None, player="Blue", split_in_two=False, start_id=32, split_in_games=True)

    #create_csv_file("fMRI-all.csv", dates, None, player="", split_in_two=False, start_id=18)
    #create_csv_file("fMRI-all.csv", dates, None, player="Blue", split_in_two=False, start_id=18)
    #create_csv_file("fMRI-split-all.csv", dates, None, player="Blue", split_in_two=True, start_id=18)

    create_csv_file("fMRI-2702-split-4.csv", dates_2702, None, player="Blue", split_in_two=False, start_id=18, split_in_games=False, split_no=4)
    create_csv_file("fMRI-0503-split-4.csv", dates_0503, None, player="Blue", split_in_two=False, start_id=21, split_in_games=False, split_no=4)
    create_csv_file("fMRI-1203-split-4.csv", dates_1203, None, player="Blue", split_in_two=False, start_id=25, split_in_games=False, split_no=4)
    create_csv_file("fMRI-1403-split-4.csv", dates_1403, None, player="Blue", split_in_two=False, start_id=29, split_in_games=False, split_no=4)
    create_csv_file("fMRI-1903-split-4.csv", dates_1903, None, player="Blue", split_in_two=False, start_id=31, split_in_games=False, split_no=4)
    create_csv_file("fMRI-2103-split-4.csv", dates_2103, None, player="Blue", split_in_two=False, start_id=32, split_in_games=False, split_no=4)

    create_csv_file("fMRI-split-4.csv", dates, None, player="Blue", split_in_two=False, start_id=18, split_in_games=False, split_no=4)

    # ==========================================================================

    
    