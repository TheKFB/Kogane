import json
from pathlib import Path
from Player import Player
from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
from interactions import ActionRow, Button, ButtonStyle, StringSelectMenu, spread_to_rows, Extension
from Database import get_db

class Game(Extension):

    def __init__(self, bot):
        self.connection = get_db()

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
        cur = self.connection.execute(
            "SELECT * FROM players "
            "WHERE player_name = ?",
            (player,)
        )
        result = cur.fetchall()
        await ctx.send(str(result))
    @show.autocomplete("player")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(
            choices=self.get_all_players()
        )

    # Join the Culling Games
    # YO! I'm Kogane! The deathmatch known as the Culling Game is underway inside of this barrier! Once you step inside, you're a player too! Knowing that, will you come inside anyway?
    @slash_command(name="join", description="Join the Culling Games!", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of the character to join",
        required=True,
        opt_type=OptionType.STRING
    )
    @slash_option(
        name="max_health",
        description="Max health",
        required=True,
        opt_type=OptionType.INTEGER
    )
    @slash_option(
        name="max_ce",
        description="CE Reserves",
        required=True,
        opt_type=OptionType.INTEGER,
        choices = [
            SlashCommandChoice(name="None", value = 0),
            SlashCommandChoice(name="Low", value = 100),
            SlashCommandChoice(name="Average", value = 750),
            SlashCommandChoice(name="High", value = 1150),
            SlashCommandChoice(name="Large", value = 1550),
            SlashCommandChoice(name="Immense", value = 1950)
        ]
    )
    async def join(self, ctx: SlashContext, name: str, max_health: int, max_ce: int):
        self.connection.execute(
            "INSERT INTO players (discord_name, player_name, max_health, current_health, max_CE, current_CE, defense, attack_bonus)"
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (str(ctx.author), name, max_health, max_health, max_ce, max_ce, 10, 0)
        )
        self.connection.commit()
        msg = name + " has officially joined the Culling Games!"
        await ctx.send(msg)
        # initial_d = {"discord_name": str(ctx.author), 
        #              "points_remaining": 13,
        #              "cursed_tools": [],
        #              "cursed_techniques": []}
        # player = Player(name, initial_d)
        # self.players[name] = player
        # self.json_players[name] = initial_d
        # self.update_players()
        # comp: list[ActionRow] = [
        #     ActionRow(
        #         Button(
        #             style=ButtonStyle.GREEN,
        #             label="Click Me",
        #         ),
        #         Button(
        #             style=ButtonStyle.GREEN,
        #             label="Click Me Too",
        #         )
        #     )
        # ]
        # await ctx.send(" has officially joined the Culling Games!", components=comp)

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
            SlashCommandChoice(name="max_CE", value="max_CE"),
            SlashCommandChoice(name="discord_name", value="discord_name"),
        ]
    )
    @slash_option(
        name="value",
        description="Value to update",
        required=True,
        opt_type=OptionType.STRING
    )
    async def update(self, ctx: SlashContext, name: str, criteria: str, value: str):
        if not self.is_owner(name, str(ctx.author)):
            await ctx.send("Sorry, you don't control " + name + "!")
            return
        
        # You can't use query substitution for field names, only values
        match criteria:
            case "discord_name":
                self.connection.execute(
                    "UPDATE players "
                    "SET discord_name = ? "
                    "WHERE player_name = ?",
                    (value, name)
                )
            case "max_health":
                value = int(value)
                self.connection.execute(
                    "UPDATE players "
                    "SET max_health = ?, current_health = ? "
                    "WHERE player_name = ?",
                    (value, value, name)
                )
            case "max_CE":
                value = convert_CE_limit(value)
                self.connection.execute(
                    "UPDATE players "
                    "SET max_CE = ?, current_CE = ? "
                    "WHERE player_name = ?",
                    (value, value, name)
                )
        
        self.connection.commit()
        msg = name + " has been updated: " + criteria + " = " + str(value)
        await ctx.send(msg)

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
        self.connection.execute(
            "UPDATE tools "
            "SET owner = ? "
            "WHERE tool_name = ?",
            (name, tool)
        )
        self.connection.commit()
        msg = name + " now wields " + tool + "!"
        await ctx.send(msg)

    @add_tool.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_players(str(ctx.author)))
    @add_tool.autocomplete("tool")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_available_tools())

    # Remove a cursed tool from your player
    @slash_command(name="remove_tool", description="Remove a cursed tool from your player", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of player to remove a tool from",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="tool",
        description="Name of tool to remove",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def remove_tool(self, ctx: SlashContext, name:str, tool:str):
        self.connection.execute(
            "UPDATE tools "
            "SET owner = NULL "
            "WHERE tool_name = ?",
            (tool,)
        )
        self.connection.commit()
        msg = name + " no longer wields " + tool
        await ctx.send(msg)

    @remove_tool.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_players(str(ctx.author)))
    @remove_tool.autocomplete("tool")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_tools(ctx.kwargs.get("name")))

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
        
        self.connection.execute(
            "UPDATE techniques "
            "SET owner = ? "
            "WHERE technique_name = ?",
            (name, technique)
        )
        self.connection.commit()

        msg = name + " now possesses " + technique + "!"
        await ctx.send(msg)

    @add_technique.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_players(str(ctx.author)))
    @add_technique.autocomplete("technique")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_available_techniques())

    # Remove a cursed tool from your player
    @slash_command(name="remove_technique", description="Remove a cursed technique from your player", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of player to remove a technique from",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="technique",
        description="Name of technique to remove",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def remove_technique(self, ctx: SlashContext, name: str, technique: str):
        self.connection.execute(
            "UPDATE techniques "
            "SET owner = NULL "
            "WHERE technique_name = ?",
            (technique,)
        )
        self.connection.commit()
        msg = name + " no longer posesses " + technique
        await ctx.send(msg)

    @remove_technique.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_players(str(ctx.author)))
    @remove_technique.autocomplete("technique")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_techniques(ctx.kwargs.get("name")))


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
        self.connection.execute(
            "DELETE FROM PLAYERS "
            "WHERE player_name = ?",
            (name,)
        )
        await ctx.send(name + " has officially left the Culling Games!")

    @remove.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(self.get_owned_players(str(ctx.author)))

#                       #
#   Helper Functions    #
#                       #

    def is_owner(self, name, user):
        cur = self.connection.execute(
            "SELECT * "
            "FROM players "
            "WHERE player_name = ? AND discord_name = ?",
            (name, user)
        )
        return len(cur.fetchall()) > 0
    
#                       #
# Autocomplete Returns  #
#                       #

    # For use in autocomplete lists
    def get_owned_players(self, user):
        cur = self.connection.execute(
            "SELECT player_name "
            "FROM players "
            "WHERE discord_name = ?",
            (user,)
        )
        ret = []
        for name in cur:
            ret.append({"name": name[0], "value": name[0]})

        return ret
    
    # For use in autocomplete lists
    def get_all_players(self):
        cur = self.connection.execute(
            "SELECT player_name "
            "FROM players"
        )
        ret = []
        for name in cur:
            ret.append({"name": name[0], "value": name[0]})
        return ret

    # For use in autocomplete lists
    def get_available_tools(self):
        cur = self.connection.execute(
            "SELECT tool_name "
            "FROM tools "
            "WHERE owner IS NULL"
        )
        tools = []
        for tool in cur:
            tools.append({"name": tool[0], "value": tool[0]})

        return tools
    
    def get_owned_tools(self, name):
        cur = self.connection.execute(
            "SELECT tool_name "
            "FROM tools "
            "WHERE owner = ?",
            (name,)
        )
        tools = []
        for tool in cur:
            tools.append({"name": tool[0], "value": tool[0]})
        return tools
    
    # For use in autocomplete lists
    def get_available_techniques(self):
        cur = self.connection.execute(
            "SELECT technique_name "
            "FROM techniques "
            "WHERE owner IS NULL"
        )
        techniques = []
        for tech in cur:
            techniques.append({"name": tech[0], "value": tech[0]})
        return techniques
    
    # For use in autocomplete lists
    def get_owned_techniques(self, name):
        cur = self.connection.execute(
            "SELECT technique_name "
            "FROM techniques "
            "WHERE owner = ?",
            (name,)
        )
        techniques = []
        for tech in cur:
            techniques.append({"name": tech[0], "value": tech[0]})
        return techniques

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
        