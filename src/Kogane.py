from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
from interactions import ActionRow, Button, ButtonStyle, StringSelectMenu, spread_to_rows
import random
import math
import json
from pathlib import Path
from Player import Player
from Game import Game

bot = Client(intents=Intents.DEFAULT)

game = Game(bot)

bot.load_extensions("Player.py")

# Roll a d20
@slash_command(name="roll", description="Roll a d20", scopes=[1165369533863837726])
async def roll(ctx: SlashContext):
    result = math.ceil(random.random() * 20)
    await ctx.send("Your result is: " + str(result))

@slash_command(name="stop", description="Stop the bot!", scopes=[1165369533863837726])
async def stop(ctx: SlashContext):
    bot.stop()
#bot.load_extension("Game")
bot.start("")
