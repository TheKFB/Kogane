from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
from interactions import ActionRow, Button, ButtonStyle, StringSelectMenu, spread_to_rows, Extension
from Database import get_db
from dice import roll
from Helpers import *
from FightTracker import *

class Combat(Extension):

    fights = {}

    def __init__(self, bot):
        self.connection = get_db()
        self.connection.row_factory = dict_factory

    # Start a fight
    @slash_command(name="start_fight", description="Begin a fight!", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of the fight, following the format 'The battle of [name]'",
        required=True,
        opt_type=OptionType.STRING
    )
    async def start_fight(self, ctx: SlashContext, name: str):
        fight = FightTracker()
        self.fights[name] = fight
        msg = f"The battle of {name} has begun!"
        await ctx.send(msg)

    # Join a fight
    @slash_command(name="join_fight", description="Join a fight!", scopes=[1165369533863837726])
    @slash_option(
        name="name",
        description="Name of the fight to join",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def join_fight(self, ctx: SlashContext, name:str):
        player = current_player(str(ctx.author))

        self.connection.execute(
            "UPDATE active_players "
            "SET fight_name = ? "
            "WHERE player_name = ?",
            (name, player)
        )
        self.connection.commit()

        initiative = roll("1d10")[0]
        self.fights[name].join_fight(player, initiative)
        msg = f"{player} has joined the battle of {name} at initiative count {initiative}!"
        await ctx.send(msg)

    @join_fight.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send([x for x in self.fights])

    # Attack a player
    @slash_command(name="attack", description="Attack another player!", scopes=[1165369533863837726])
    @slash_option(
        name="target",
        description="Target to attack",
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
    async def attack(self, ctx: SlashContext, target: str, weapon: str, cursed_energy: int = 0, description: str = "attack"):
        attacker = current_player(str(ctx.author))
        # 25 CE = 10 damage, verify CE is a multiple of 25
        if cursed_energy % 25 != 0 or cursed_energy < 0 :
            msg = "Sorry, you put in " + str(cursed_energy) + " cursed energy, but it has to be a multiple of 25! (0, 25, 50, etc)"
            await ctx.send(msg)
            return
        
        # Verify player has enough CE for what they want to do
        if not verify_cursed_energy(attacker, cursed_energy):
            msg = "Sorry, you tried to use " + cursed_energy + " CE but don't have enough!"
            await ctx.send(msg)
            return
        
        drain_cursed_energy(attacker, cursed_energy)
        
        cur = self.connection.execute(
            "SELECT attack_bonus "
            "FROM players "
            "WHERE player_name = ?",
            (attacker,)
        )
        attack_bonus = cur.fetchone()["attack_bonus"]
        roll_value = roll("1d20")[0]
        total = roll_value + attack_bonus
        roll_string = f"**1d20 + {attack_bonus} = {roll_value} + {attack_bonus} = {total}**\n"
        await ctx.send(roll_string)
        cur.close()

        cur = self.connection.execute(
            "SELECT defense "
            "FROM players "
            "WHERE player_name = ?",
            (target,)
        )
        target_defense = cur.fetchone()["defense"]
        success = total > target_defense
        msg = f"{attacker} tries to {description}"
        cur.close()

        if not success:
            msg += f", but fails!"
            final_msg = roll_string + msg
            await ctx.send(final_msg)
            return
        
        damage = 0
        damagestr = ""
        rollres = 0

        if weapon != "martial arts":
            cur = self.connection.execute(
                "SELECT damage "
                "FROM tools "
                "WHERE tool_name = ?",
                (weapon,)
            )
            damagestr = cur.fetchone()["damage"]
            rollres = roll(damagestr)
            damage += rollres
            cur.close()

        # 25 CE = 10 damage
        ce_damage = cursed_energy / 2.5
        damage += ce_damage

        deal_damage(target, damage)
        msg += f" and succeeds, dealing **{str(damagestr)} ({rollres}) + {ce_damage:.0f} = {damage:.0f}** damage!"
        final_msg = roll_string + msg
        await ctx.send(final_msg)
    
    @attack.autocomplete("target")
    async def autocomplete(self, ctx: AutocompleteContext):
        attacker = current_player(str(ctx.author))
        fight_name = get_player_fight(attacker)
        await ctx.send(choices=get_players_in_fight(fight_name))

    @attack.autocomplete("weapon")
    async def autocomplete(self, ctx: AutocompleteContext):
        choices = get_owned_tools(current_player(str(ctx.author)))
        choices.append("martial arts")
        await ctx.send(choices)

    #Use a cursed technique
    @slash_command("activate_technique", description="Activate a cursed technique!", scopes=[1165369533863837726])
    @slash_option(
        name="target",
        description="Target of the technique",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    @slash_option(
        name="technique",
        description="Technique to use",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def activate_technique(self, ctx: SlashContext, target: str, technique: str):
        user = current_player(str(ctx.author))
        cur = self.connection.execute(
            "SELECT damage, CE_cost "
            "FROM techniques "
            "WHERE technique_name = ?",
            (technique,)
        )
        res = cur.fetchone()
        cost = res["CE_cost"]
        cur.close()

        if not verify_cursed_energy(user, cost):
            msg = "Sorry, you tried to use " + cost + " CE but don't have enough!"
            await ctx.send(msg)
            return

        drain_cursed_energy(user, cost)
        damage = roll(res["damage"])
        deal_damage(target, damage)

        # Get technique buffs/debuffs
        cur = self.connection.execute(
            "SELECT modified_field, modified_value, duration "
            "FROM modifiers "
            "WHERE technique_name = ?",
            (technique,)
        )
        results = cur.fetchall()
        cur.close()

        # Apply technique buffs/debuffs
        fight_name = get_player_fight(target)
        for mod in results:
            value = roll(mod["modified_value"])
            duration = roll(mod["duration"])
            self.fights[fight_name].add_buff(target, mod["modified_field"], value, duration)

        msg = f"{user} activates their cursed technique: {technique} on {target}!"
        await ctx.send(msg)

    @activate_technique.autocomplete("target")
    async def autocomplete(self, ctx: AutocompleteContext):
        attacker = current_player(str(ctx.author))
        fight_name = get_player_fight(attacker)
        await ctx.send(get_players_in_fight(fight_name))

    @activate_technique.autocomplete("technique")
    async def autocomplete(self, ctx: AutocompleteContext):
        user = current_player(str(ctx.author))
        await ctx.send(get_owned_techniques(user))

    #reinforce with CE
    @slash_command(name="reinforce_defense", description="Imbue yourself with cursed energy to increase your defense")
    @slash_option(
        name="cursed_energy",
        description="Amount of cursed energy to imbue (multiple of 25)",
        required=True,
        opt_type=OptionType.INTEGER
    )
    async def reinforce_defense(self, ctx: SlashContext, cursed_energy: int):
        player = current_player(str(ctx.author))
        # 25 CE = +2 defense, verify CE is a multiple of 25
        if cursed_energy % 25 != 0 or cursed_energy < 0 :
            msg = "Sorry, you put in " + str(cursed_energy) + " cursed energy, but it has to be a multiple of 25! (0, 25, 50, etc)"
            await ctx.send(msg)
            return
        
        # Verify player has enough CE for what they want to do
        if not verify_cursed_energy(player, cursed_energy):
            msg = "Sorry, you tried to use " + cursed_energy + " CE but don't have enough!"
            await ctx.send(msg)
            return

        

        

        
