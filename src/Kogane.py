from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
import random
import math
import json
from pathlib import Path
from Player import Player
from Game import Game

bot = Client(intents=Intents.DEFAULT)

game = Game()

# Roll a d20
@slash_command(name="roll", description="Roll a d20", scopes=[1165369533863837726])
async def roll(ctx: SlashContext):
    result = math.ceil(random.random() * 20)
    await ctx.send("Your result is: " + str(result))

# Show a player's stats
@slash_command(name="show", description="Show a player's information", scopes=[1165369533863837726])
@slash_option(
    name="player",
    description="Show a Player's stats",
    required=True,
    opt_type=OptionType.STRING
)
async def show(ctx: SlashContext, player: str):
    await ctx.send(game.get_player(player))

# Join the Culling Games
# YO! I'm Kogane! The deathmatch known as the CUlling Game is underway inside of this barrier! Once you step inside, you're a player too! Knowing that, will you come inside anyway?
@slash_command(name="join", description="Join the Culling Games!", scopes=[1165369533863837726])
@slash_option(
    name="name",
    description="Name of the character to join",
    required=True,
    opt_type=OptionType.STRING
)
async def join(ctx: SlashContext, name: str):
    game.add_player(name, ctx.author)
    await ctx.send(name + " has officially joined the Culling Games!")

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
    opt_type=OptionType.STRING
)
async def update(ctx: SlashContext, name: str, criteria: str, value: str):
    if not game.is_owner(name, str(ctx.author)):
        await ctx.send("Sorry, you don't control " + name + "!")
        return
    game.update_player(name, criteria, value)
    await ctx.send(name + " has been updated: " + criteria + " = " + value)

@update.autocomplete("name")
async def autocomplete(ctx: AutocompleteContext):
    await ctx.send(
        choices=[{"name": name, "value": name} for name in game.json_players]
    )

# Remove a player from the Culling Games
@slash_command(name="remove", description="Remove a player from the Culling Games!", scopes=[1165369533863837726])
@slash_option(
    name="name",
    description="Name of player to remove",
    required=True,
    opt_type=OptionType.STRING
)
async def remove(ctx: SlashContext, name: str):
    if not game.is_owner(name, str(ctx.author)):
        await ctx.send("Sorry, you don't control " + name + "!")
        return
    game.remove_player(name)
    await ctx.send(name + " has officially left the Culling Games!")

bot.start()
