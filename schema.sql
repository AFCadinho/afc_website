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
    name TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);



INSERT INTO users(name, password) 
VALUES('putra', 'Libra148'); 

INSERT INTO users(name, password, is_admin) 
VALUES('adinho', 'Gambler2010', TRUE); 

-- Game Table
CREATE TABLE game (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);


INSERT INTO game(name) 
VALUES ('pokemmo');

-- Teams table
CREATE TABLE pokemmo_teams (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES game(id),
    name TEXT NOT NULL,
    pokepaste TEXT NOT NULL UNIQUE
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
(1, 'ARCANINE ENTERS OU', 'https://pokepast.es/7b2f7c2fa6065676'),
(1, 'MegaMoltres Duo Dual Defog', 'https://pokepast.es/b93d8a152ef16589');

-- Insert Pokémon for teams
INSERT INTO pokemon(team_id, name)
VALUES
-- Pokémon for Arcanine team
(1, 'Arcanine'), (1, 'Metagross'), (1, 'Rotom-Wash'), (1, 'Gliscor'), (1, 'Chansey'), (1, 'Gallade'),
-- Pokémon for Moltres team
(2, 'Yanmega'), (2, 'Scizor'), (2, 'Moltres'), (2, 'Gallade'), (2, 'Garchomp'), (2, 'Dragonite');
