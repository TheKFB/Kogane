from interactions import Client, Intents, slash_command, slash_option, OptionType, SlashContext, SlashCommandChoice, AutocompleteContext
from interactions import ActionRow, Button, ButtonStyle, StringSelectMenu, spread_to_rows, Extension, Embed
from Database import get_db
from dice import roll
from Helpers import *
from FightTracker import *

class Combat(Extension):


    def __init__(self, bot):
        self.connection = get_db()
        self.connection.row_factory = dict_factory
        bot.fights = {}

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
        self.bot.fights[name] = fight
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
            "UPDATE players "
            "SET fight_name = ? "
            "WHERE player_name = ?",
            (name, player)
        )
        self.connection.commit()

        initiative = roll("1d10")[0]
        self.bot.fights[name].join_fight(player, initiative)

        cur = self.connection.execute(
            "SELECT * "
            "FROM heavenly_restrictions "
            "WHERE player_name = ?",
            (player,)
        )

        for hr in cur.fetchall():
            buff = Modifier("Heavenly Restriction", hr["buff_category"], hr["buff_value"], 999)
            debuff = Modifier("Heavenly Restriction", hr["debuff_category"], hr["debuff_value"], 999)
            self.bot.fights[name].add_modifier(player, buff)
            self.bot.fights[name].add_modifier(player, debuff)

        cur.close()
        msg = f"{player} has joined the battle of {name} at initiative count {initiative}!"
        await ctx.send(msg)

    @join_fight.autocomplete("name")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send([x for x in self.bot.fights])

    # Advance the turn order
    @slash_command(name="end_turn", description="End your turn", scopes=[1165369533863837726])
    async def end_turn(self, ctx: SlashContext):
        player = current_player(str(ctx.author))
        fight = get_player_fight(player)
        self.bot.fights[fight].next_turn()
        new_player = self.bot.fights[fight].current_player()
        msg = f"It is now {new_player}'s turn!"
        await ctx.send(msg)

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
        fight = get_player_fight(attacker)
        # 25 CE = 10 damage, verify CE is a multiple of 25
        if cursed_energy % 25 != 0 or cursed_energy < 0 :
            msg = "Sorry, you put in " + str(cursed_energy) + " cursed energy, but it has to be a multiple of 25! (0, 25, 50, etc)"
            await ctx.send(msg)
            return
        
        # Verify player has enough CE for what they want to do
        ver_str = verify_cursed_energy(attacker, self.bot.fights[fight], cursed_energy)
        if ver_str != "":
            await ctx.send(ver_str)
            return
        
        self.bot.fights[fight].participants[attacker].CE_used += cursed_energy
        modify_cursed_energy(attacker, -cursed_energy)
        
        attack_bonus = self.bot.fights[fight].participants[attacker].get_modifier("attack")
        roll_value = roll("1d20")[0]
        total = roll_value + attack_bonus
        roll_string = f"**1d20 + {attack_bonus} = {roll_value} + {attack_bonus} = {total}**\n"
        await ctx.send(roll_string)

        target_defense = 10 + self.bot.fights[fight].participants[target].get_modifier("defense")
        success = total > target_defense
        msg = f"{attacker} tries to {description}"

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
        fight_name = get_player_fight(target)
        cur = self.connection.execute(
            "SELECT damage, CE_cost "
            "FROM techniques "
            "WHERE technique_name = ?",
            (technique,)
        )
        res = cur.fetchone()
        cost = res["CE_cost"]
        cur.close()

        # Verify player has enough CE for what they want to do
        ver_str = verify_cursed_energy(user, self.bot.fights[fight_name], cost)
        if ver_str != "":
            await ctx.send(ver_str)
            return

        self.bot.fights[fight_name].participants[user].CE_used += cost
        modify_cursed_energy(user, -cost)
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
        for mod in results:
            value = mod["modified_value"]
            duration = roll(mod["duration"])
            new_mod = Modifier(technique, mod["modified_field"], value, duration)
            
            self.bot.fights[fight_name].add_modifier(target, new_mod)

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
    @slash_command(name="reinforce_defense", description="Imbue yourself with cursed energy to increase your defense", scopes=[1165369533863837726])
    @slash_option(
        name="cursed_energy",
        description="Amount of cursed energy to imbue (multiple of 25)",
        required=True,
        opt_type=OptionType.INTEGER
    )
    async def reinforce_defense(self, ctx: SlashContext, cursed_energy: int):
        player = current_player(str(ctx.author))
        fight = get_player_fight(player)
        # 25 CE = +2 defense, verify CE is a multiple of 25
        if cursed_energy % 25 != 0 or cursed_energy < 0 :
            msg = f"Sorry, you put in {cursed_energy} cursed energy, but it has to be a multiple of 25! (0, 25, 50, etc)"
            await ctx.send(msg)
            return
        
        # Verify player has enough CE for what they want to do
        ver_str = verify_cursed_energy(player, self.bot.fights[fight], cursed_energy)
        if ver_str != "":
            await ctx.send(ver_str)
            return

        self.bot.fights[fight].participants[player].CE_used += cursed_energy
        modify_cursed_energy(player, -cursed_energy)

        defense_mod = cursed_energy / 12.5
        reinforce_buff = Modifier("Reinforcement", "defense", defense_mod, 1)
        self.bot.fights[fight].add_modifier(player, reinforce_buff)
        msg = f"{player} reinforces themselves with cursed energy, increasing their defense by {defense_mod:.0f}!"
        await ctx.send(msg)
        
    #Chant to regain CE and increase CE max
    @slash_command(name="chant", description="Increase CE and CE max", scopes=[1165369533863837726])
    async def chant(self, ctx: SlashContext):
        player = current_player(str(ctx.author))
        fight = get_player_fight(player)

        modify_cursed_energy(player, 100)
        chant_buff = Modifier("Chanting", "CE_max", 50, 1)
        self.bot.fights[fight].add_modifier(player, chant_buff)
        msg = f"{player} chants, restoring their cursed energy!"
        await ctx.send(msg)

    #Use RCT to heal self or other (with output RCT)
    @slash_command(name="rct", description="Use reverse cursed technique", scopes=[1165369533863837726])
    @slash_option(
        name="target",
        description="Player to output RCT on",
        required=False,
        opt_type=OptionType.INTEGER,
        autocomplete=True
    )
    async def rct(self, ctx: SlashContext, target: str = "none"):
        user = current_player(str(ctx.author))
        fight = get_player_fight(user)
        cost = 50
        restore = 10
        
        cur = self.connection.execute(
            "SELECT * "
            "FROM rct "
            "WHERE player_name = ?",
            (user,)
        )
        rct_result = cur.fetchone()
        cur.close()

        if rct_result is None:
            msg = f"Sorry, but you don't know how to use RCT!"
            await ctx.send(msg)
            return

        if target != "none":
            if rct_result["output_rct"] == 1:
                target = user
            else:
                msg = f"Sorry, but you don't know how to output RCT!"
                await ctx.send(msg)
                return
        else:
            target = user
            
        if rct_result["fast_healing"]:
            restore = 15

        # Verify player has enough CE for what they want to do
        ver_str = verify_cursed_energy(user, self.bot.fights[fight], cost)
        if ver_str != "":
            await ctx.send(ver_str)
            return
        
        self.bot.fights[fight].participants[user].CE_used += cost
        modify_cursed_energy(user, cost)
        restore_health(target, restore)

        msg = f"{user} healed {target} for {restore} health!"
        await ctx.send(msg)

    @rct.autocomplete("target")
    async def autocomplete(self, ctx: AutocompleteContext):
        user = current_player(str(ctx.author))
        fight_name = get_player_fight(user)
        await ctx.send(get_players_in_fight(fight_name))

    #Show initiative
    @slash_command(name="show_fight", description="Show the turn order of a fight", scopes=[1165369533863837726])
    @slash_option(
        name="fight",
        description="Name of fight to show",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True
    )
    async def show_fight(self, ctx: SlashContext, fight: str):
        title = f"The battle of {fight}"
        desc = self.bot.fights[fight].list_initiative()
        e = Embed(title=title, description=desc)
        await ctx.send(embed=e)

    @show_fight.autocomplete("fight")
    async def autocomplete(self, ctx: AutocompleteContext):
        await ctx.send([x for x in self.bot.fights])

        
        

        
