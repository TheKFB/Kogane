from dice import roll

class Participant():
    name = ""
    initiative = 0
    cooldowns = {}

    def __init__(self, player_name, init):
        self.name = player_name
        self.initiative = init

    def lower_cooldowns(self):
        for cd in self.cooldowns:
            self.cooldowns[cd] -= 1

            if self.cooldowns[cd] == 0:
                del self.cooldowns[cd]

    def add_buff(self, category, value, duration):
        key = category + ":" + str(value)
        #Cooldowns decrement at the start of a player's turn, so a 1-round buff needs
        #To have a duration of 1+1=2 so i
        self.cooldowns[key] = duration + 1

    def get_bonus(self, category):
        bonus_str = ""
        #Ability cooldowns are formatted like {"name": cooldown}
        #While buffs are {"category:value": duration}
        for bonus in self.cooldowns:
            split = bonus.split(":")
            if len(split) < 2:
                continue
            if split[0] != category:
                continue
            bonus_str += split[1]

        result = roll(bonus_str)[0]

        return result

class FightTracker():
    # Key: player_name, Value: Participant
    participants = {}
    turn_order = []
    current_turn = 0

    def add_buff(self, target, category, value, duration):
        self.participants[target].add_buff(category, value, duration)

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