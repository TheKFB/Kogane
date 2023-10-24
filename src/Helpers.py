from Database import get_db

connection = get_db()

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
    return len(cur.fetchall()) > 0

# TODO: implement damage reduction
def deal_damage(name, damage):
    cur = connection.execute(
        "SELECT current_health "
        "FROM players "
        "WHERE player_name = ?",
        (name,)
    )
    current_health = cur.fetchone()[0] - damage

    cur = connection.execute(
        "UPDATE players "
        "SET current_health = ? "
        "WHERE player_name = ?",
        (current_health, name)
    )
    connection.commit()

def verify_cursed_energy(name, amount):
    cur = connection.execute(
        "SELECT current_CE "
        "FROM players "
        "WHERE player_name = ?",
        (name,)
    )
    current_energy = cur.fetchone()[0]
    return current_energy >= amount

def drain_cursed_energy(name, amount):
    cur = connection.execute(
        "SELECT current_CE "
        "FROM players "
        "WHERE player_name = ?",
        (name,)
    )
    new_energy = cur.fetchone()[0] - amount

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
    ret = []
    for name in cur:
        ret.append({"name": name[0], "value": name[0]})

    return ret

def get_all_players():
    cur = connection.execute(
        "SELECT player_name "
        "FROM players"
    )
    ret = []
    for name in cur:
        ret.append({"name": name[0], "value": name[0]})
    return ret

def get_available_tools():
    cur = connection.execute(
        "SELECT tool_name "
        "FROM tools "
        "WHERE owner IS NULL"
    )
    tools = []
    for tool in cur:
        tools.append({"name": tool[0], "value": tool[0]})

    return tools

def get_owned_tools(name):
    cur = connection.execute(
        "SELECT tool_name "
        "FROM tools "
        "WHERE owner = ?",
        (name,)
    )
    tools = []
    for tool in cur:
        tools.append({"name": tool[0], "value": tool[0]})
    return tools

def get_available_techniques():
    cur = connection.execute(
        "SELECT technique_name "
        "FROM techniques "
        "WHERE owner IS NULL"
    )
    techniques = []
    for tech in cur:
        techniques.append({"name": tech[0], "value": tech[0]})
    return techniques


def get_owned_techniques(name):
    cur = connection.execute(
        "SELECT technique_name "
        "FROM techniques "
        "WHERE owner = ?",
        (name,)
    )
    techniques = []
    for tech in cur:
        techniques.append({"name": tech[0], "value": tech[0]})
    return techniques
