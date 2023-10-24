from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
from interactions import ActionRow, Button, ButtonStyle, StringSelectMenu, spread_to_rows, Extension
from Database import get_db
from dice import roll
from Helpers import *

class Combat(Extension):

    def __init__(self, bot):
        self.connection = get_db()

    @slash_command(name="attack", description="Attack another player!", scopes=[1165369533863837726])
    @slash_option(
        name="player",
        description="Player who is attacking",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="weapon",
        description="Weapon to attack with",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="target",
        description="Target to attack",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="cursed_energy",
        description="How much Cursed Energy to imbue your attack with",
        required=False,
        opt_type=OptionType.INTEGER
    )
    @slash_option(
        name="description",
        description="A flavorful description of your attack which completes the sentence: [Player Name] tries to...",
        required=False,
        opt_type = OptionType.STRING
    )
    async def attack(self, ctx: SlashContext, player: str, weapon: str, target: str, cursed_energy: int = 0, description: str = "attack"):
        # 25 CE = 10 damage, verify CE is a multiple of 25
        if cursed_energy % 25 != 0 or cursed_energy < 0 :
            msg = "Sorry, you put in " + str(cursed_energy) + " cursed energy, but it has to be a multiple of 25! (0, 25, 50, etc)"
            await ctx.send(msg)
            return
        
        # Verify player has enough CE for what they want to do
        if not verify_cursed_energy(player, cursed_energy):
            msg = "Sorry, you tried to use " + cursed_energy + " CE but don't have enough!"
            await ctx.send(msg)
            return
        
        cur = self.connection.execute(
            "SELECT attack_bonus "
            "FROM players "
            "WHERE player_name = ?",
            (player,)
        )
        attack_bonus = cur.fetchone()[0]
        roll_value = roll("1d20")[0]
        total = roll_value + attack_bonus

        cur = self.connection.execute(
            "SELECT defense "
            "FROM players "
            "WHERE player_name = ?",
            (target,)
        )
        target_defense = cur.fetchone()[0]
        success = total > target_defense
        msg = player + " tries to " + description

        if not success:
            msg = msg + ", but fails!"
            await ctx.send(msg)
            return
        
        damage = 0

        if weapon != "martial arts":
            cur = self.connection.execute(
                "SELECT damage "
                "FROM tools "
                "WHERE tool_name = ?",
                (weapon,)
            )

            damage += cur.fetchone()[0]

        # 25 CE = 10 damage
        damage += cursed_energy / 2.5

        deal_damage(target, damage)
        drain_cursed_energy(player, cursed_energy)
        msg = msg + ", and succeeds!"
        await ctx.send(msg)
        
    @attack.autocomplete("player")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(choices=get_owned_players(str(ctx.author)))
    
    @attack.autocomplete("weapon")
    async def autocomplete(self, ctx: AutocompleteContext):
        choices = get_owned_tools(ctx.kwargs.get("player"))
        choices.append({"name": "martial arts", "value": "martial arts"})
        await ctx.send(choices)

    @attack.autocomplete("target")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send(choices=get_all_players())

        

        
