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
        initial_d = {"discord_name": str(user), 
                     "points_remaining": 13,
                     "cursed_tools": [],
                     "cursed_techniques": []}
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

    def add_tool(self, name, tool):
        self.json_players[name]["cursed_tools"].append(tool)
        self.players[name].info = self.json_players[name]
        self.update_players()

    def add_technique(self, name, technique):
        self.json_players[name]["cursed_techniques"].append(technique)
        self.players[name].info = self.json_players[name]
        self.update_players()

    def remove_player(self, name):
        del self.players[name]
        del self.json_players[name]
        self.update_players()

    # For use in autocomplete lists
    def get_owned_players(self, user):
        choices = []
        for name in self.json_players:
            if self.is_owner(name, user):
                choices.append({"name": name, "value": name})
        return choices
    
    # For use in autocomplete lists
    def get_all_players(self):
        return [{"name": name, "value": name} for name in self.json_players]

    # For use in autocomplete lists
    def get_available_tools(self):
        used_tools = []
        for player in self.json_players:
            for tool in self.json_players[player]["cursed_tools"]:
                used_tools.append(tool)

        available_tools = []
        for tool in self.json_tools:
            if tool not in used_tools:
                available_tools.append({"name": tool, "value": tool})

        return available_tools
    
    # For use in autocomplete lists
    def get_available_techniques(self):
        used_techniques = []
        for player in self.json_players:
            for technique in self.json_players[player]["cursed_techniques"]:
                used_techniques.append(technique)

        # Cursed tools with a cursed technique have the technique that is the same name as the tool
        # This makes sure you can't add a tool's technique as a player technique
        cursed_tools = [x for x in self.json_tools]
        available_techniques = []
        for technique in self.json_techniques:
            if technique not in used_techniques and technique not in cursed_tools:
                available_techniques.append({"name": technique, "value": technique})

        return available_techniques
    
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
        