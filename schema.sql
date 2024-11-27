-- wsl
-- source .venv/bin/activate
-- poetry run postgresqlite < schema.sql
-- poetry run postgresqlite pgcli



-- Drop schema if exists
DROP SCHEMA IF EXISTS public CASCADE;

-- Create schema
CREATE SCHEMA public;

-- Create tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    password TEXT NOT NULL
);

INSERT INTO users(name, password) VALUES('Adinho', 'Gambler2010');
INSERT INTO users(name, password) VALUES('Putra', 'Libra148');

-- Game Table
CREATE TABLE game (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);


INSERT INTO game(name) 
VALUES ('pokemmo');

-- Teams table
CREATE TABLE pokemmo_teams (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES game(id),
    name TEXT NOT NULL,
    pokepaste TEXT NOT NULL
);

-- Team members table
CREATE TABLE pokemon (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES pokemmo_teams(id),
    name TEXT NOT NULL
);

-- Insert sample teams
INSERT INTO pokemmo_teams(game_id, name, pokepaste)
VALUES
(1, 'Arcanine', 'https://pokepast.es/7b2f7c2fa6065676'),
(1, 'Moltres', 'https://pokepast.es/b93d8a152ef16589');

-- Insert Pokémon for teams
INSERT INTO pokemon(team_id, name)
VALUES
-- Pokémon for Arcanine team
(1, 'Arcanine'), (1, 'Metagross'), (1, 'Rotom-Wash'), (1, 'Gliscor'), (1, 'Chansey'), (1, 'Gallade'),
-- Pokémon for Moltres team
(2, 'Yanmega'), (2, 'Scizor'), (2, 'Moltres'), (2, 'Gallade'), (2, 'Garchomp'), (2, 'Dragonite');
