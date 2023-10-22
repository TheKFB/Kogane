class Player:
    character_name = ""
    info = {}
    # discord_name = ""
    # max_health = 0
    # current_health = 0
    # max_cursed_energy = 0
    # current_cursed_energy = 0
    # cursed_tools = []
    # cursed_techniques = []

    def __init__(self, name, info):
        self.character_name = name
        self.info = info
        # self.discord_name = info["discord_name"]
        # self.max_health = info["max_health"]
        # self.current_health = info["current_health"]
        # self.max_cursed_energy = convert_CE_limit(info["max_cursed_energy"])
        # self.current_cursed_energy = info["current_cursed_energy"]
        # self.cursed_tools = info["cursed_tools"]
        # self.cursed_techniques = info["cursed_techniques"]

    def __str__(self):
        return (f"Culling Games Player {self.info['character_name']}\n" 
                f"Health: {self.info['current_health']}/{self.info['max_health']}\n"
                f"Cursed Energy: {self.info['current_cursed_energy']}/{self.info['max_cursed_energy']}\n"
                f"Cursed Tools: {self.info['cursed_tools']}\n"
                f"Cursed Techniques: {self.info['cursed_techniques']}\n"
        )

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