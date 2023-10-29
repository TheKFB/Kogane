PRAGMA foreign_keys = ON;

CREATE TABLE players(
    discord_name VARCHAR(40) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    max_health INTEGER NOT NULL,
    current_health INTEGER NOT NULL,
    max_CE INTEGER NOT NULL,
    current_CE INTEGER NOT NULL,
    fight_name VARCHAR(100),
    PRIMARY KEY(player_name)
);

CREATE TABLE active_players(
    discord_name VARCHAR(40) NOT NULL UNIQUE,
    player_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (player_name) REFERENCES players(player_name),
    PRIMARY KEY (discord_name)
);

CREATE TABLE techniques(
    technique_name VARCHAR(100) NOT NULL,
    CE_cost INTEGER NOT NULL,
    damage VARCHAR(40) NOT NULL,
    activation_type VARCHAR(40) NOT NULL,
    owner VARCHAR(100),
    FOREIGN KEY (owner) REFERENCES players(player_name),
    PRIMARY KEY(technique_name)
);

CREATE TABLE modifiers(
    id INTEGER PRIMARY KEY,
    technique_name VARCHAR(100) NOT NULL,
    modified_field VARCHAR(40) NOT NULL,
    modified_value VARCHAR(40) NOT NULL,
    duration VARCHAR(40) NOT NULL,
    FOREIGN KEY (technique_name) REFERENCES techniques(technique_name)
);

CREATE TABLE tools(
    tool_name VARCHAR(100) NOT NULL,
    point_cost INTEGER NOT NULL,
    damage VARCHAR(40) NOT NULL,
    technique_name VARCHAR(100),
    owner VARCHAR(100),
    FOREIGN KEY (technique_name) REFERENCES techniques(technique_name),
    FOREIGN KEY (owner) REFERENCES players(player_name),
    PRIMARY KEY(tool_name)
);

CREATE TABLE domains(
    domain_name VARCHAR(100) NOT NULL,
    owner VARCHAR (100) NOT NULL,
    CE_cost INTEGER NOT NULL,
    sure_hit INTEGER NOT NULL,
    point_two_activation INTEGER NOT NULL,
    enhanced_barrior INTEGER NOT NULL,
    targets_objects INTEGER NOT NULL,
    amplification INTEGER NOT NULL,
    FOREIGN KEY (owner) REFERENCES players(player_name),
    PRIMARY KEY (domain_name)
);

CREATE TABLE rct(
    player_name VARCHAR(100) NOT NULL,
    counter_poison INTEGER NOT NULL, 
    fast_healing INTEGER NOT NULL,
    output_rct INTEGER NOT NULL,
    FOREIGN KEY (player_name) REFERENCES players(player_name),
    PRIMARY KEY (player_name)
);

CREATE TABLE heavenly_restrictions(
    player_name VARCHAR(100) NOT NULL,
    full_restriction INTEGER NOT NULL,
    buff_category VARCHAR(40) NOT NULL,
    buff_value VARCHAR(40) NOT NULL,
    debuff_category VARCHAR(40) NOT NULL,
    debuff_value VARCAHR(40) NOT NULL,
    FOREIGN KEY (player_name) REFERENCES players(player_name),
    PRIMARY KEY (player_name)
);

PRAGMA foreign_key_check;
