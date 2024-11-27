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

CREATE TABLE pokemmo_teams (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    pokepaste TEXT NOT NULL
);
