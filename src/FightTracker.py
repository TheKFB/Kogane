from dice import roll

class Modifier():

    def __init__(self, name, category, value, duration):
        self.name = name    #Source of the modification
        self.category = category    #Valid categories: attack, defense, damage_resistance, CE_max, attack_CE_max
        self.value = value  #Amount of modification. A string, which can be a single number or dice expression
        self.duration = duration    #In number of rounds

class Participant():
    name = ""
    initiative = 0

    #Max CE you can use in a turn
    CE_max = 100
    #Max CE you can use on an attack
    attack_CE_max = 50
    CE_used = 0
    #List of modifiers
    modifiers = []

    def __init__(self, player_name, init):
        self.name = player_name
        self.initiative = init

    def lower_cooldowns(self):
        finished_cooldowns = []
        for mod in self.modifiers:
            mod.duration -= 1

            if mod.duration == 0:
                finished_cooldowns.append(mod)

        for ele in finished_cooldowns:
            self.modifiers.remove(ele)

    def add_modifier(self, name, category, value, duration):
        #Cooldowns decrement at the start of a player's turn, so a 1-round buff needs
        #To have a duration of 1+1=2 so i
        mod = Modifier(name, category, value, duration + 1)
        self.modifiers.append(mod)

    def get_modifier(self, category):
        bonus_str = ""

        for mod in self.modifiers:
            if mod.category != category:
                continue
            else:
                bonus_str += mod.value

        result = roll(bonus_str)[0]

        return result
    
    def get_modifier_str(self, category):
        bonus_str = ""

        for mod in self.modifiers:
            if mod.category != category:
                continue
            else:
                bonus_str += f"\t{mod.name}: {mod.value} ({mod.duration} round(s) left)\n"  

        return bonus_str

class FightTracker():
    # Key: player_name, Value: Participant
    participants = {}
    turn_order = []
    current_turn = 0

    def add_modifier(self, target, name, category, value, duration):
        self.participants[target].add_modifier(name, category, value, duration)

    def join_fight(self, player, init):
        self.participants[player] = Participant(player, init)

        # Insert player above the first player they have a higher initiative than
        for idx, participant in enumerate(self.turn_order):
            if init > self.participants[participant].initiative:
                self.turn_order.insert(idx, player)
        # If they are the first or slowest, just append to the end
        if player not in self.turn_order:
            self.turn_order.append(player)

    def next_turn(self):
        self.current_turn += 1
        if self.current_turn >= len(self.turn_order):
            self.current_turn = 0

        # lower cooldowns of next player
        self.participants[self.turn_order[self.current_turn]].lower_cooldowns()
        # reset CE amount used
        self.participants[self.turn_order[self.current_turn]].CE_used = 0

    def current_player(self):
        return self.turn_order[self.current_turn]