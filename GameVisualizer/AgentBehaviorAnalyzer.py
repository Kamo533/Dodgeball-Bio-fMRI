import math
import pandas as pd

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

    def __init__(self, date="2024-02-07_14-44-25", subfolder="", fsm=False):
        self.date = date
        self.player_data = PlayerData(getLogData("PlayerData", date, subfolder))
        self.position_data = PositionData(getLogData("Position", date, subfolder))
        self.results_data = getLogData("Results", date, subfolder)
        if fsm : y_delta = 0
        else : y_delta = 34
        self.zones = define_zones(define_corners(y_delta=y_delta, margin=0.5), 1,2)
        self.bushes = define_bushes(y_delta=y_delta)


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
        for pos_entry in self.position_data.pos_list:
            dist_sum += math.dist(self.get_position(pos_entry, "Blue"), self.get_position(pos_entry, "Purple"))
        return dist_sum/len(self.position_data.pos_list)


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

        return list(filter(lambda pos: is_facing(pos, agent, margin_degrees) and no_obstacles(pos, agent), self.position_data.pos_list))
    

    def calculate_percentage_facing_opponent(self, agent="Blue", margin_degrees=10):
        """
        Calculate the fraction of time spent facing the opponent.
        margin_degrees is how many degrees agent can be rotated away from opponent while still being considered facing the opponent.
        """
        facing_list = self.get_instances_of_facing_opponent(agent)
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
        Return the zone where the agent is in the beginning of the game.
        """
        timestamp = self.position_data.pos_list[0].timestamp
        return self.find_agent_zone(timestamp, agent)
    

    def calculate_average_pickup_throw_time(self, agent="Blue"):
        """
        Calculate the how long it takes on average for the agent to throw the ball after pickup.
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
        Calculate the percentage of the movements that are a rotation change in the opposite direction.
        AI agents tend to have more jerky movements and thus a higher percentage.
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
        close_list = list(filter(lambda pos: (self.is_close_to_bush(pos.timestamp, agent, distance)), self.position_data.pos_list))
        return len(close_list)/len(self.position_data.pos_list)



    def calculate_hiding_percentage(self, agent="Blue"):
        """
        Calculate the percentage of time the agent spends hiding from the opponent behind a bush.
        """
        hiding_count = 0
        for pos_entry in self.position_data.pos_list:
            pos = self.get_position(pos_entry, agent)
            pos_opponent = self.get_opponent_position(pos_entry, agent)
            for bush in self.bushes:
                bush_start, bush_end = bush[0], bush[-1]
                # Is hiding if the line between the agents is crossing the bush and the agent is close to that bush
                if lines_crossing(pos, pos_opponent, bush_start, bush_end) and close_to_bush(pos, bush):
                    hiding_count += 1
        return hiding_count/len(self.position_data.pos_list)

    

    def count_wins(self, agent="Blue"):
        """
        Count how many times the agent won a game.
        """
        iterator = iter(self.results_data.splitlines())
        count = 0
        for result_line in iterator:
            data = result_line.split(",")
            if "Winner: " + agent in data[1]:
                count += 1
        return count
    

    def count_move_away(self, agent="Blue", pos_list=[]):
        """
        Count how many time intervals the agent moves away from its opponent.
        """
        move_away_count = 0
        prev_pos_entry = pos_list[0]
        prev_distance = self.calculate_distance_between_agents(prev_pos_entry.timestamp)
        prev_opponent_pos = self.get_opponent_position(prev_pos_entry, agent)
        for pos_entry in pos_list[1:]:
            pos = self.get_position(pos_entry, agent)
            new_distance = math.dist(pos, prev_opponent_pos)
            if new_distance > prev_distance:
                move_away_count += 1
            prev_distance = self.calculate_distance_between_agents(pos_entry.timestamp)
            prev_opponent_pos = self.get_opponent_position(pos_entry, agent)
        return move_away_count

    
    def find_move_away_percentage(self, agent="Blue"):
        """
        Calculate the percentage of time the agent spends moving away from its opponent.
        """
        move_away_count = self.count_move_away(agent, self.position_data.pos_list)
        return move_away_count/len(self.position_data.pos_list)
    

    def calculate_move_away_when_facing_opponent(self, agent="Blue", margin_degrees=20):
        """
        Calculate the percentage of time the agent spends moving away from its opponent when it sees the opponent.
        """
        facing_list = self.get_instances_of_facing_opponent(agent, margin_degrees)
        move_away_count = 0
        prev_pos_entry = facing_list[0]
        sub_facing_list = []
        for pos_entry in facing_list:
            if pos_entry.timestamp - prev_pos_entry.timestamp < pd.Timedelta(seconds=1):
                sub_facing_list.append(pos_entry)
            elif len(sub_facing_list) > 1:
                move_away_count += self.count_move_away(agent, sub_facing_list)
                sub_facing_list = []
            else:
                sub_facing_list = []
            prev_pos_entry = pos_entry
        return move_away_count/len(facing_list)



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

        # print("Percentage of time Blue is close to a bush:", round(self.calculate_bush_closeness_percentage("Blue", 3)*100, 3), "%")
        # print("Percentage of time Purple is close to a bush:", round(self.calculate_bush_closeness_percentage("Purple")*100, 3), "%")



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

    """ print("Moves away".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.find_move_away_percentage(agent)*100, 3)} %'.ljust(spacing), end="")
    print() """

    print("Moves away facing".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_move_away_when_facing_opponent(agent)*100, 3)} %'.ljust(spacing), end="")
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

    """ print("On blue side".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_zone_percentage(agent)[(1,0)]*100, 3)} %'.ljust(spacing), end="")
    print()

    print("On purple side".ljust(spacing+extra_spacing), end="")
    for a in analyzers:
        print(f'{round(a.calculate_zone_percentage(agent)[(0,0)]*100, 3)} %'.ljust(spacing), end="")
    print() """

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


def print_playstyle_table(dates={}, agent="Purple", subfolder=""):
    """
    Show an overview of each agent and how similar its playstyle is to each of the other agents' playstyles
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


def add_data_analyzer(date, subfolder=""):
    da = DataAnalyzer(subfolder)
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


def compare_multiple_agents(dates={}, agent="Purple", subfolder=""):
    analyzers = []
    da_analyzers = []
    for game in dates.keys():
        if "FSM" in game: analyzer = AgentBehaviorAnalyzer(dates[game], subfolder, fsm=True)
        else : analyzer = AgentBehaviorAnalyzer(dates[game], subfolder)
        da_analyzer = add_data_analyzer(dates[game], subfolder)
        analyzers.append(analyzer)
        da_analyzers.append(da_analyzer)
    print_divider()
    compare(analyzers, da_analyzers, dates.keys(), agent)


def show_study_results(date_list=[{}], agent="Purple", subfolder=""):
    i = 1
    for dates in date_list:
        print_divider()
        print("USER", i, "---", agent)
        print_divider()
        compare_multiple_agents(dates, agent, subfolder)
        i += 1



if __name__ == "__main__":

    # ====================== Pre study ==========================

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

    # show_study_results([dates_pre_study], "Purple", "/PreStudy")
    # print_playstyle_table(dates_pre_study, "Purple", "/PreStudy")

    # ===========================================================


    # ====================== Pilot study ========================

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
    show_study_results(dates_pilot, "Purple", "/PilotStudy")

    # ===========================================================


    # ======================= (Pilot) Experiments =======================

    dates_fmri_1 = {
        "FSM": "2024-02-13_19-19-16",
        "RL": "2024-02-13_19-05-14"
    }

    dates_fmri_2 = {
        "FSM": "2024-02-13_20-22-08",
        "RL": "2024-02-13_20-36-09"
    }

    # show_study_results([dates_fmri_1, dates_fmri_2], "Purple", "/fMRI")
    # show_study_results([dates_fmri_1, dates_fmri_2], "Blue", "/fMRI")

    # =========================================================


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

    # ======================================================================

    fsm_rl_five_balls = {
        "FSM 4": "2024-02-25_13-55-29",
        "FSM 5": "2024-02-25_14-10-21"
    }

    # show_study_results([fsm_rl_five_balls], "Blue", "/FSM-RL")
    # show_study_results([fsm_rl_five_balls], "Purple", "/FSM-RL")

    fsm_rl_four_balls = {
        "FSM 4": "2024-02-25_21-10-02",
        "FSM 5": "2024-02-25_21-21-02"
    }

    # show_study_results([fsm_rl_four_balls], "Blue", "/FSM-RL")
    # show_study_results([fsm_rl_four_balls], "Purple", "/FSM-RL")
    
    five_balls = {
        "FSM 4": "2024-02-25_21-49-40",
        "FSM 5": "2024-02-25_21-57-06",
        "RL": "2024-02-25_22-04-26"
    }

    # show_study_results([five_balls], "Purple", "/Analyze/FSM-4")

    four_balls = {
        "FSM 4": "2024-02-25_22-13-32",
        "FSM 5": "2024-02-25_22-28-52",
        "RL": "2024-02-25_22-20-20"
    }

    # show_study_results([four_balls], "Purple", "/Analyze/FSM-4")

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
        "7.0 throw chance": "2024-02-26_14-44-42"
    }

    # show_study_results([fsm_rl_4_7], "Blue", "/FSM-RL")
    # show_study_results([fsm_rl_4_7], "Purple", "/FSM-RL")
    
    
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

    show_study_results([elen, sindre], "Purple", "/ElenTest")
    show_study_results([elen, sindre], "Blue", "/ElenTest")

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

    
    

