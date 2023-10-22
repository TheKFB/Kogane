import json
from pathlib import Path
from Player import Player

class Game:
    # Dict of Player objects
    # Format: "name": Player_Object
    players = {}

    json_players = {}

    json_tools = {}

    json_techniques = {}

    def __init__(self):
        self.load_players()

    def load_players(self):
        self.read_data()

        for name, info in self.json_players.items():
            player = Player(name, info)
            self.players[name] = player

    def get_player(self, name):
        return str(self.players[name])
    
    def add_player(self, name, user):
        initial_d = {"discord_name": str(user), "points_remaining": 13}
        player = Player(name, initial_d)
        self.players[name] = player
        self.json_players[name] = initial_d
        self.update_players()

    def is_owner(self, name, user):
        return user == self.json_players[name]["discord_name"]

    def update_player(self, name, criteria, value):
        match criteria:
            case "max_health":
                value = int(value)
                self.json_players[name]["current_health"] = value
            case "max_cursed_energy":
                value = convert_CE_limit(value)
                self.json_players[name]["current_cursed_energy"] = value

        self.json_players[name][criteria] = value
    
        self.players[name].info = self.json_players[name]
        self.update_players()

    def remove_player(self, name):
        del self.players[name]
        del self.json_players[name]
        self.update_players()

    # Load .json files into game
    def read_data(self):
        cur_path = Path(__file__).parent
        players_path = cur_path / "../json/players.json"
        f = open(players_path, "r")
        self.json_players = json.loads(f.read())
        f.close()

        tools_path = cur_path / "../json/cursed_warehouse.json"
        f = open(tools_path, "r")
        self.json_tools = json.loads(f.read())
        f.close()

        techniques_path = cur_path / "../json/cursed_techniques.json"
        f = open(techniques_path, "r")
        self.json_techniques = json.loads(f.read())
        f.close()
    
    # Updates players.json
    def update_players(self):
        self.update_data("players")

    # Updates cursed_warehouse.json
    def update_tools(self):
        self.update_data("cursed_warehouse")

    # Updates cursed_techniques.json
    def update_techniques(self):
        self.update_data("cursed_techniques")
    
    # Updates an arbitrary JSON file
    def update_data(self, name):
        cur_path = Path(__file__).parent
        file = str(name) + ".json"
        path = cur_path / "../json/" / file
        f = open(path, "w")
        match name:
            case "players":
                f.write(json.dumps(self.json_players, sort_keys=True, indent=4))
            case "cursed_warehouse":
                f.write(json.dumps(self.json_tools, sort_keys=True, indent=4))
            case "cursed_techniques":
                f.write(json.dumps(self.json_techniques, sort_keys=True, indent=4))
        f.close()

def convert_CE_limit(limit):
    match limit:
        case "none":
            return 0
        case "low":
            return 100
        case "average":
            return 750
        case "high":
            return 1150
        case "large":
            return 1550
        case "immense":
            return 1950
        