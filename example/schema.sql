-- To (re)create a database with this schema, use the following shell command:
-- poetry run postgresqlite < schema.sql 

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;


CREATE TABLE player (
    id serial NOT NULL PRIMARY KEY,
    name text NOT NULL,
    password text NOT NULL
);

INSERT INTO player(name, password) VALUES('Test', 'ilovemum');


CREATE TABLE game (
    id serial NOT NULL PRIMARY KEY,
    player_id integer NOT NULL REFERENCES player(id),
    secret text NOT NULL,
    "time" timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    result integer
);


CREATE TABLE guess (
    id serial NOT NULL PRIMARY KEY,
    game_id integer NOT NULL REFERENCES game(id),
    word text NOT NULL,
    "time" timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
