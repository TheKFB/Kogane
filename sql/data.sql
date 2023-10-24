PRAGMA foreign_keys = ON;

INSERT INTO players(discord_name, player_name, max_health, current_health, max_CE, current_CE, defense, attack_bonus)
VALUES ('@thekidfrombrooklyn.com', 'Aoi Todo', 200, 200, 1950, 1950, 10, 0);

INSERT INTO techniques(technique_name, CE_cost, owner)
VALUES ('Playful Cloud', 0, 'Aoi Todo');

INSERT INTO techniques(technique_name, CE_cost)
VALUES ('Boogie Woogie', 50);

INSERT INTO tools(tool_name, point_cost, damage, technique_name, owner)
VALUES ('Playful Cloud', 3, 0, 'Playful Cloud', 'Aoi Todo');

INSERT INTO tools(tool_name, point_cost, damage)
VALUES ('Slaughter Demon', 1, 10);