PRAGMA foreign_keys = ON;

CREATE TABLE players(
    discord_name VARCHAR(40) NOT NULL,
    player_name VARCHAR(100) NOT NULL,
    max_health INTEGER NOT NULL,
    current_health INTEGER NOT NULL,
    max_CE INTEGER NOT NULL,
    current_CE INTEGER NOT NULL,
    defense INTEGER NOT NULL,
    attack_bonus INTEGER NOT NULL,
    PRIMARY KEY(player_name)
);

CREATE TABLE techniques(
    technique_name VARCHAR(100) NOT NULL,
    CE_cost INTEGER NOT NULL,
    owner VARCHAR(100) NOT NULL,
    FOREIGN KEY (owner) REFERENCES players(player_name),
    PRIMARY KEY(technique_name)
);

CREATE TABLE tools(
    tool_name VARCHAR(100) NOT NULL,
    point_cost INTEGER NOT NULL,
    damage INTEGER NOT NULL,
    technique_name VARCHAR(100) NOT NULL,
    owner VARCHAR(40) NOT NULL,
    FOREIGN KEY (technique_name) REFERENCES techniques(technique_name),
    FOREIGN KEY (owner) REFERENCES players(player_name),
    PRIMARY KEY(tool_name)
);