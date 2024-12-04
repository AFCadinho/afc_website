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
VALUES('putra', '$2b$12$yrnWC8yUkkhuPAKb.QTeL.zlMCqD5rH2dql1TQJZF.xmoJhsAKhaC'); 

INSERT INTO users(name, password, is_admin) 
VALUES('adinho', '$2b$12$j1l8HthnWaFygkd92x4L1uPl0dT4R3vR/YSB6Pc2El/FjZ8EN.vOu', TRUE);

-- Game Table
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);


INSERT INTO games(name) 
VALUES 
('pokemmo'),
('pokemon blaze online'),
('pokemon brick bronze');


-- Teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES games(id),
    name TEXT NOT NULL,
    pokepaste TEXT NOT NULL UNIQUE,
    created_at DATE DEFAULT CURRENT_DATE NOT NULL
);

-- Team members table
CREATE TABLE pokemon (
    id SERIAL PRIMARY KEY,
    team_id INTEGER NOT NULL REFERENCES teams(id),
    name TEXT NOT NULL
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- -- Insert sample teams
-- INSERT INTO teams(game_id, name, pokepaste)
-- VALUES
-- (1, 'ARCANINE ENTERS OU', 'https://pokepast.es/7b2f7c2fa6065676'),
-- (1, 'MegaMoltres Duo Dual Defog', 'https://pokepast.es/b93d8a152ef16589'),
-- (2, 'UU Intermediate Dual Pivot Spin', 'https://pokepast.es/4df3080c5a8af1b9'),
-- (3, 'Lopunny Boost Draga HO', 'https://pokepast.es/e88f7c237ffdff96');

-- -- Insert Pokémon for teams
-- INSERT INTO pokemon(team_id, name)
-- VALUES
-- -- Pokémon for Arcanine team
-- (1, 'Arcanine'), (1, 'Metagross'), (1, 'Rotom-Wash'), (1, 'Gliscor'), (1, 'Chansey'), (1, 'Gallade'),
-- -- Pokémon for Moltres team
-- (2, 'Yanmega'), (2, 'Scizor'), (2, 'Moltres'), (2, 'Gallade'), (2, 'Garchomp'), (2, 'Dragonite');
