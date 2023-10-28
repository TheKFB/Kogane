PRAGMA foreign_keys = ON;

INSERT INTO players(discord_name, player_name, max_health, current_health, max_CE, current_CE)
VALUES ('@thekidfrombrooklyn.com', 'Aoi Todo', 200, 200, 1950, 1950);

INSERT INTO players(discord_name, player_name, max_health, current_health, max_CE, current_CE)
VALUES ('@thekidfrombrooklyn.com', 'Killua Zoldyk', 100, 100, 750, 750);

INSERT INTO active_players(discord_name, player_name)
VALUES ('@thekidfrombrooklyn.com', 'Aoi Todo');

INSERT INTO techniques(technique_name, CE_cost, damage)
VALUES ('Boogie Woogie', 50, '0');

INSERT INTO rct(player_name, counter_poison, fast_healing, output_rct)
VALUES ('Aoi Todo', 0, 0, 0);

INSERT INTO modifiers(technique_name, modified_field, modified_value, duration)
VALUES ('Boogie Woogie', 'defense', '2', '1');

INSERT INTO modifiers(technique_name, modified_field, modified_value, duration)
VALUES ('Boogie Woogie', 'attack', '2', '1');

INSERT INTO tools(tool_name, point_cost, damage, owner)
VALUES ('Playful Cloud', 3, '1d3*10', 'Aoi Todo');

INSERT INTO tools(tool_name, point_cost, damage)
VALUES ('Slaughter Demon', 1, '10');