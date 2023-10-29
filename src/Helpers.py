from Database import get_db

# Used when configuring a connection to have cursors return dicts instead of lists
def dict_factory(cur, row):
    d = {}
    for idx, col in enumerate(cur.description):
        d[col[0]] = row[idx]
    return d

connection = get_db()
connection.row_factory = dict_factory

#                       #
#   Helper Functions    #
#                       #

def is_owner(name, user):
    cur = connection.execute(
        "SELECT * "
        "FROM players "
        "WHERE player_name = ? AND discord_name = ?",
        (name, user)
    )
    result = cur.fetchall()
    cur.close()
    return len(result) > 0

def current_player(user):
    cur = connection.execute(
        "SELECT player_name "
        "FROM active_players "
        "WHERE discord_name = ?",
        (user,)
    )
    result = cur.fetchone()["player_name"]
    cur.close()
    return result

def get_player_fight(player):
    cur = connection.execute(
        "SELECT fight_name "
        "FROM players "
        "WHERE player_name = ?",
        (player,)
    )
    result = cur.fetchone()["fight_name"]
    cur.close()
    return result

# TODO: implement damage reduction
def deal_damage(name, damage):
    cur = connection.execute(
        "SELECT current_health "
        "FROM players "
        "WHERE player_name = ?",
        (name,)
    )
    current_health = cur.fetchone()["current_health"] - damage
    cur.close()

    cur = connection.execute(
        "UPDATE players "
        "SET current_health = ? "
        "WHERE player_name = ?",
        (current_health, name)
    )
    connection.commit()
    cur.close()

def restore_health(name, health):
    cur = connection.execute(
        "SELECT current_health, max_health "
        "FROM players "
        "WHERE player_name = ?",
        (name,)
    )
    h = cur.fetchone()
    cur.close()
    new_health = h["current_health"] + health
    max_health = h["max_health"]

    if new_health > max_health:
        new_health = max_health

    connection.execute(
        "UPDATE players "
        "SET current_health = ? "
        "WHERE player_name = ?",
        (new_health, name)
    )
    connection.commit()

def verify_cursed_energy(name, amount):
    cur = connection.execute(
        "SELECT current_CE "
        "FROM players "
        "WHERE player_name = ?",
        (name,)
    )
    current_energy = cur.fetchone()
    cur.close()
    current_energy = current_energy["current_CE"]
    return current_energy >= amount

def modify_cursed_energy(name, amount):
    cur = connection.execute(
        "SELECT current_CE, max_CE "
        "FROM players "
        "WHERE player_name = ?",
        (name,)
    )
    energy = cur.fetchone()
    new_energy = energy["current_CE"] + amount
    max_energy = energy["max_CE"]

    # Make sure not to overcap energy. Shouldn't need a lower bound... surely this will not bite me in the future
    if new_energy > max_energy:
        new_energy = max_energy

    cur.close()

    connection.execute(
        "UPDATE players "
        "SET current_CE = ? "
        "WHERE player_name = ?",
        (new_energy, name)
    )
    connection.commit()

def convert_CE_limit(limit):
    match limit:
        case "none":
            return 0
        case "low":
            return 100
        case "average":
            return 750
        case "high":
            return 1150
        case "large":
            return 1550
        case "immense":
            return 1950
    
#                       #
# Autocomplete Returns  #
#                       #

def get_owned_players(user):
    cur = connection.execute(
        "SELECT player_name "
        "FROM players "
        "WHERE discord_name = ?",
        (user,)
    )
    ret = [name["player_name"] for name in cur]
    cur.close()
    return ret

def get_all_players():
    cur = connection.execute(
        "SELECT player_name "
        "FROM players"
    )
    ret = [name["player_name"] for name in cur]
    cur.close()
    return ret

def get_available_tools():
    cur = connection.execute(
        "SELECT tool_name "
        "FROM tools "
        "WHERE owner IS NULL"
    )
    tools = [tool["tool_name"] for tool in cur]
    cur.close()
    return tools

def get_owned_tools(name):
    cur = connection.execute(
        "SELECT tool_name "
        "FROM tools "
        "WHERE owner = ?",
        (name,)
    )
    tools = [tool["tool_name"] for tool in cur]
    cur.close()
    return tools

def get_available_techniques():
    cur = connection.execute(
        "SELECT technique_name "
        "FROM techniques "
        "WHERE owner IS NULL"
    )
    techniques = [technique["technique_name"] for technique in cur]
    cur.close()
    return techniques


def get_owned_techniques(name):
    cur = connection.execute(
        "SELECT technique_name "
        "FROM techniques "
        "WHERE owner = ?",
        (name,)
    )
    techniques = [technique["technique_name"] for technique in cur]
    cur.close()
    return techniques

def get_players_in_fight(name):
    cur = connection.execute(
        "SELECT player_name "
        "FROM players "
        "WHERE fight_name = ?",
        (name,)
    )
    players = [player["player_name"] for player in cur]
    cur.close()
    return players
