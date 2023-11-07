from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
from interactions import ActionRow, Button, ButtonStyle, StringSelectMenu, spread_to_rows, Extension
from Database import get_db
from Helpers import *

class Game(Extension):

    def __init__(self, bot):
        self.connection = get_db()
        self.connection.row_factory = dict_factory

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
        result = cur.fetchone()
        cur.close()

        cur = connection.execute(
            "SELECT tool_name "
            "FROM tools "
            "WHERE owner = ?",
            (player,)
        )
        tools = cur.fetchall()
        cur.close()

        cur = connection.execute(
            "SELECT technique_name "
            "FROM techniques "
            "WHERE owner = ?",
            (player,)
        )
        techniques = cur.fetchall()
        cur.close()

        cur = connection.execute(
            "SELECT fight_name "
            "FROM players "
            "WHERE player_name = ?",
            (player,)
        )
        fight_res = cur.fetchone()
        cur.close()


        msg = f"Player: {result['player_name']}\n"
        msg += f"Controlled by: {result['discord_name']}\n"
        msg += f"Health: {result['current_health']}/{result['max_health']}\n"
        msg += f"Cursed Energy: {result['current_CE']}/{result['max_CE']}\n"
        
        if tools != None:
            msg += f"Tools:\n"
            for tool in tools:
                msg += f"\t{tool['tool_name']}\n"

        if techniques != None:
            msg += f"Techniques:\n"
            for tech in techniques:
                msg += f"\t{tech['technique_name']}\n"

        if fight_res != None:
            msg += f"{player} is currently fighting in {fight_res['fight_name']}!\n"
            msg += f"Active modifiers:\n"
            for category in ["attack", "defense", "damage_resistance", "CE_max", "attack_CE_max"]:
                cat_str = self.bot.fights[fight_res['fight_name']].participants[player].get_modifier_str(category)
                #Skip if no active modifier in category
                if cat_str == "":
                    continue
                msg += f"{category}\n"
                msg += f"{cat_str}\n"

        await ctx.send(msg)
    @show.autocomplete("player")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(
            choices=get_all_players()
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
        if(max_health < 1):
            await ctx.send("Sorry, but your max health must be at least 1!")
            return

        self.connection.execute(
            "INSERT INTO players (discord_name, player_name, max_health, current_health, max_CE, current_CE) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (str(ctx.author), name, max_health, max_health, max_ce, max_ce)
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
    async def update(self, ctx: SlashContext, criteria: str, value: str):
        name = current_player(str(ctx.author))
        if not is_owner(name, str(ctx.author)):
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
                if(value < 1):
                    await ctx.send("Sorry, but your max health must be at least 1!")
                    return
                
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

    # Add a cursed tool to your player!
    @slash_command(name="add_tool", description="Add a cursed tool to your player!", scopes=[1165369533863837726])
    @slash_option(
        name="tool",
        description="Name of tool to give",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def add_tool(self, ctx: SlashContext, tool: str):
        name = current_player(str(ctx.author))
        if not is_owner(name, str(ctx.author)):
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

    @add_tool.autocomplete("tool")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(get_available_tools())

    # Remove a cursed tool from your player
    @slash_command(name="remove_tool", description="Remove a cursed tool from your player", scopes=[1165369533863837726])
    @slash_option(
        name="tool",
        description="Name of tool to remove",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def remove_tool(self, ctx: SlashContext, tool:str):
        name = current_player(str(ctx.author))
        self.connection.execute(
            "UPDATE tools "
            "SET owner = NULL "
            "WHERE tool_name = ?",
            (tool,)
        )
        self.connection.commit()
        msg = name + " no longer wields " + tool
        await ctx.send(msg)

    @remove_tool.autocomplete("tool")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(get_owned_tools(ctx.kwargs.get("name")))

    # Add a cursed technique to your player!
    @slash_command(name="add_technique", description="Add a cursed technique to your player!", scopes=[1165369533863837726])
    @slash_option(
        name="technique",
        description="Name of technique to give",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def add_technique(self, ctx: SlashContext, technique: str):
        name = current_player(str(ctx.author))
        if not is_owner(name, str(ctx.author)):
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

    @add_technique.autocomplete("technique")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(get_available_techniques())

    # Remove a cursed tool from your player
    @slash_command(name="remove_technique", description="Remove a cursed technique from your player", scopes=[1165369533863837726])
    @slash_option(
        name="technique",
        description="Name of technique to remove",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def remove_technique(self, ctx: SlashContext, technique: str):
        name = current_player(str(ctx.author))
        self.connection.execute(
            "UPDATE techniques "
            "SET owner = NULL "
            "WHERE technique_name = ?",
            (technique,)
        )
        self.connection.commit()
        msg = name + " no longer posesses " + technique
        await ctx.send(msg)

    @remove_technique.autocomplete("technique")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(get_owned_techniques(ctx.kwargs.get("name")))

    # Switch active player
    @slash_command(name="change_player", description="Change which player you are using", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of player to switch to",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def change_player(self, ctx: SlashContext, name: str):
        self.connection.execute(
            "UPDATE active_players "
            "SET player_name = ? "
            "WHERE discord_name = ?",
            (name, str(ctx.author))
        )
        self.connection.commit()
        msg = f"Now controlling {name}"
        await ctx.send(msg)

    @change_player.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(get_owned_players(str(ctx.author)))

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
        if not is_owner(name, str(ctx.author)):
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
        await ctx.send(get_owned_players(str(ctx.author)))
        