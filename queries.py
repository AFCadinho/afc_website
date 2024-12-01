def check_username(db, name):
    name = db.query_row("""
                        SELECT *
                        FROM users
                        WHERE name = :name
                        """, name=name)
    print(name)
    return name


def insert_user(db, name, password, is_admin=False):
    if is_admin == False:
        is_admin = "FALSE"
    else:
        is_admin = "TRUE"

    db.execute("""
            INSERT INTO users(name, password, is_admin)
            VALUES (:name, :password, :is_admin)
            """, {"name": name, "password": password, "is_admin": is_admin})


def get_user_id(db, name):
    return db.query_value("""
                SELECT id
                FROM users
                WHERE name = :name
                """, name=name)


def get_all_games(db):
    return db.query_column("""
            SELECT name
            FROM games
            """)


def get_game_id(db, name):
    return db.query_value("""
                    SELECT id
                    FROM games
                    WHERE name = :name
                    """, name=name)


def get_all_teams_from_game(db, game_id, release_year):
    start_date = f"{release_year}-01-01"
    end_date = f"{release_year + 1}-01-01"

    return db.query("""
                SELECT *
                FROM teams
                WHERE game_id = :game_id AND created_at >= :start_date AND created_at < :end_date
            """, game_id=game_id, start_date=start_date, end_date=end_date)


def get_all_teams_data(db):
    return db.query("""
        SELECT *
        FROM teams
        """)


def insert_data_into_teams(db, data):
    for row in data:
        db.execute(
            """
            INSERT INTO teams (id, game_id, name, pokepaste, created_at)
            VALUES (:id, :game_id, :name, :pokepaste, :created_at)
            ON CONFLICT (id) DO NOTHING
            """,
            {
                "id": row["id"],
                "game_id": row["game_id"],
                "name": row["name"],
                "pokepaste": row["pokepaste"],
                "created_at": row["created_at"]
            }
        )
