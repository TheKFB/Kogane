import json
from pathlib import Path
from Player import Player
from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
from interactions import ActionRow, Button, ButtonStyle, StringSelectMenu, spread_to_rows, Extension

class Game(Extension):
    # Dict of Player objects
    # Format: "name": Player_Object
    players = {}

    json_players = {}

    json_tools = {}

    json_techniques = {}

    def __init__(self, bot):
        self.load_players()

    def load_players(self):
        self.read_data()

        for name, info in self.json_players.items():
            player = Player(name, info)
            self.players[name] = player

#                   #
#   Slash Commands  #
#                   #

    # Show a player's stats
    @slash_command(name="show", description="Show a player's information", scopes=[1165369533863837726])
    @slash_option(
        name="player",
        description="Show a Player's stats",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def show(self, ctx: SlashContext, player: str):
        await ctx.send(str(json.dumps(self.json_players[player], indent=4)))
    @show.autocomplete("player")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(
            choices=self.get_all_players()
        )

    # Join the Culling Games
    # YO! I'm Kogane! The deathmatch known as the CUlling Game is underway inside of this barrier! Once you step inside, you're a player too! Knowing that, will you come inside anyway?
    @slash_command(name="join", description="Join the Culling Games!", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of the character to join",
        required=True,
        opt_type=OptionType.STRING
    )
    async def join(self, ctx: SlashContext, name: str):
        initial_d = {"discord_name": str(ctx.author), 
                     "points_remaining": 13,
                     "cursed_tools": [],
                     "cursed_techniques": []}
        player = Player(name, initial_d)
        self.players[name] = player
        self.json_players[name] = initial_d
        self.update_players()
        comp: list[ActionRow] = [
            ActionRow(
                Button(
                    style=ButtonStyle.GREEN,
                    label="Click Me",
                ),
                Button(
                    style=ButtonStyle.GREEN,
                    label="Click Me Too",
                )
            )
        ]
        await ctx.send(" has officially joined the Culling Games!", components=comp)

    # Update a Player
    @slash_command(name="update", description="Update your player", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of the character to update",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="criteria",
        description="Criteria to update",
        required=True,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name="max_health", value="max_health"),
            SlashCommandChoice(name="max_cursed_energy", value="max_cursed_energy"),
            SlashCommandChoice(name="discord_name", value="discord_name"),
        ]
    )
    @slash_option(
        name="value",
        description="Value to update",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def update(self, ctx: SlashContext, name: str, criteria: str, value: str):
        if not self.is_owner(name, str(ctx.author)):
            await ctx.send("Sorry, you don't control " + name + "!")
            return
        
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
        await ctx.send(name + " has been updated: " + criteria + " = " + str(value))

    @update.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(
            choices=self.get_owned_players(str(ctx.author))
        )

    # Add a cursed tool to your player!
    @slash_command(name="add_tool", description="Add a cursed tool to your player!", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of player to give a tool",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="tool",
        description="Name of tool to give",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def add_tool(self, ctx: SlashContext, name: str, tool: str):
        if not self.is_owner(name, str(ctx.author)):
            await ctx.send("Sorry, you don't control " + name + "!")
            return
        self.json_players[name]["cursed_tools"].append(tool)
        self.players[name].info = self.json_players[name]
        self.update_players()
        await ctx.send(name + " now wields " + tool + "!")

    @add_tool.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_players(str(ctx.author)))
    @add_tool.autocomplete("tool")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_available_tools())

    # Add a cursed technique to your player!
    @slash_command(name="add_technique", description="Add a cursed technique to your player!", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of player to give a technique",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="technique",
        description="Name of technique to give",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def add_technique(self, ctx: SlashContext, name: str, technique: str):
        if not self.is_owner(name, str(ctx.author)):
            await ctx.send("Sorry, you don't control " + name + "!")
            return
        self.json_players[name]["cursed_techniques"].append(technique)
        self.players[name].info = self.json_players[name]
        self.update_players()
        await ctx.send(name + " now possesses " + technique + "!")

    @add_technique.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_players(str(ctx.author)))
    @add_technique.autocomplete("technique")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_available_techniques())

    # Remove a player from the Culling Games
    @slash_command(name="remove", description="Remove a player from the Culling Games!", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of player to remove",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def remove(self, ctx: SlashContext, name: str):
        if not self.is_owner(name, str(ctx.author)):
            await ctx.send("Sorry, you don't control " + name + "!")
            return
        del self.players[name]
        del self.json_players[name]
        self.update_players()
        await ctx.send(name + " has officially left the Culling Games!")

    @remove.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_players(str(ctx.author)))

#                       #
#   Helper Functions    #
#                       #

    def is_owner(self, name, user):
        return user == self.json_players[name]["discord_name"]

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
        