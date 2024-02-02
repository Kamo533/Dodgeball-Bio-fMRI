import math

from GameVisualizer import PlayerData, PositionData, getLogData


date = "2024-01-30_15-46-27"

y_delta = 34
margin = 0

corners = [(8.9 - margin, -20 + y_delta + margin), (34.9 + margin, -20 + y_delta + margin),
        (34.9 + margin, round(-73.9 + y_delta, 2) - margin), (8.9 - margin, round(-73.9 + y_delta, 2) - margin)]

bushes = [
    [(18.8, -64.5 + y_delta), (13.3, -64.5 + y_delta)],
    [(32.0, -64.5 + y_delta), (26.5, -64.5 + y_delta)],
    [(18.3, -54.6 + y_delta), (14.4, -58.5 + y_delta)],
    [(29.8, -58.5 + y_delta), (25.9, -54.6 + y_delta)],
    [(18.8, -42.8 + y_delta), (14.9, -38.9 + y_delta)],
    [(29.3, -38.9 + y_delta), (25.4, -42.8 + y_delta)],
    [(18.8, -31.9 + y_delta), (13.3, -31.9 + y_delta)],
    [(32.0, -31.7 + y_delta), (26.5, -31.7 + y_delta)],
]


def define_zones(breadth_no=3, length_no=3):
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

    def __init__(self):
        self.player_data = PlayerData(getLogData("PlayerData", date))
        self.position_data = PositionData(getLogData("Position", date))
        self.results_data = getLogData("Results")
        self.zones = define_zones()


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
    

    def calculate_percentage_facing_opponent(self, agent="Blue"):
        """
        Calculate the fraction of time spent facing the opponent.
        """
        facing_list = list(filter(lambda pos: (self.calculate_rotation_difference(pos.timestamp, agent) < 10), self.position_data.pos_list))
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
            is_in_x = pos[0] > min_max_dict["min_x"] and pos[0] < min_max_dict["max_x"]
            is_in_y = pos[1] > min_max_dict["min_y"] and pos[1] < min_max_dict["max_y"]
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


    def is_hiding(self, agent="Blue"):
        return False

    
    
if __name__ == "__main__":
    ba = AgentBehaviorAnalyzer()
    # print(ba.calculate_average_throw_distance("Blue"))
    # print(ba.calculate_average_throw_distance("Purple"))
    # print(ba.calculate_rotation_difference(ta.position_data.pos_list[0].timestamp, agent="Purple"))
    # print(ba.calculate_average_throw_angle("Blue"))
    # print(ba.calculate_average_throw_angle("Purple"))
    # print(ba.calculate_angle_when_hit("Purple"))
    # print(ba.calculate_angle_when_hit("Blue"))
    # print("Blue", ba.calculate_percentage_facing_opponent("Blue")*100)
    # print("Purple", ba.calculate_percentage_facing_opponent("Purple")*100)

    # print(define_zones())
    print(ba.calculate_zone_percentage("Blue"))
    print(ba.calculate_zone_percentage("Purple"))

