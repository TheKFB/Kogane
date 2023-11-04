from dice import roll

class Modifier():

    def __init__(self, name, category, value, duration):
        self.name = name    #Source of the modification
        self.category = category    #Valid categories: attack, defense, damage_resistance, CE_max, attack_CE_max
        self.value = value  #Amount of modification. A string, which can be a single number or dice expression
        self.duration = duration    #In number of rounds

    #def __str__(self):
    #    return f"Name: {self.name}, Category: {self.category}, Value: {self.value}, Duration: {self.duration}"

class Participant():

    def __init__(self, player_name, init):
        self.name = player_name
        self.initiative = init

        #Max CE you can use in a turn
        self.CE_max = 100
        #Max CE you can use on an attack
        self.attack_CE_max = 50
        self.CE_used = 0
        #List of modifiers
        self.modifiers = []

    def lower_cooldowns(self):
        finished_cooldowns = []
        for mod in self.modifiers:
            mod.duration -= 1

            if mod.duration == 0:
                finished_cooldowns.append(mod)

        for ele in finished_cooldowns:
            self.modifiers.remove(ele)

    def add_modifier(self, new_mod):
        self.modifiers.append(new_mod)

    def get_modifier(self, category):
        bonus_str = ""

        for mod in self.modifiers:
            if mod.category != category:
                continue
            else:
                bonus_str += mod.value

        if bonus_str == "":
            return 0
        else:
            return roll(bonus_str)[0]
    
    def get_modifier_str(self, category):
        bonus_str = ""

        for mod in self.modifiers:
            if mod.category != category:
                continue
            else:
                bonus_str += f"\t{mod.name}: {mod.value} ({mod.duration} round(s) left)\n"  

        return bonus_str

class FightTracker():

    def __init__(self):
        # Key: player_name, Value: Participant
        self.participants = {}
        self.turn_order = []
        self.current_turn = 0


    def add_modifier(self, target, new_mod):
        self.participants[target].add_modifier(new_mod)

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