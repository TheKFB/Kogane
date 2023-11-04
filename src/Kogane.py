from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
import random
import math
from Game import Game
from Combat import Combat
from dice import roll

bot = Client(intents=Intents.DEFAULT)

# Roll a d20
@slash_command(name="roll_die", description="Roll a die", scopes=[1165369533863837726])
@slash_option(
    name="equation",
    description="Equation",
    required=True,
    opt_type=OptionType.STRING
)
async def roll_die(ctx: SlashContext, equation: str):
    result = roll(equation)
    await ctx.send(str(result))

@slash_command(name="stop", description="Stop the bot!", scopes=[1165369533863837726])
async def stop(ctx: SlashContext):
    bot.stop()

bot.load_extension("Game")
bot.load_extension("Combat")
bot.start("")
