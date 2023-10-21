from interactions import Client, Intents, slash_command, SlashContext
import random
import math

bot = Client(intents=Intents.DEFAULT)

@slash_command(name="roll", description="Roll a d20", scopes=[1165369533863837726])
async def roll(ctx: SlashContext):
    result = math.ceil(random.random() * 20)
    await ctx.send("Your result is: " + str(result))

bot.start(")
