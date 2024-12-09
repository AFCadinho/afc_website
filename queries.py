def check_username(db, name):
    name = db.query_row("""
                        SELECT *
                        FROM users
                        WHERE name = :name
                        """, name=name)
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


def get_all_teams_from_game_release(db, game_id, release_year):
    start_date = f"{release_year}-01-01"
    end_date = f"{release_year + 1}-01-01"

    return db.query("""
                SELECT *
                FROM teams
                WHERE game_id = :game_id AND created_at >= :start_date AND created_at < :end_date
            """, game_id=game_id, start_date=start_date, end_date=end_date)


def get_all_teams_from_game_id(db, game_id):
    return db.query("""
            SELECT *
            FROM teams
            where game_id = :game_id
            """, game_id=game_id)


def get_all_teams_data(db):
    return db.query("""
        SELECT *
        FROM teams
        """)


def insert_csv_into_teams(db, data):
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

    # Update the sequence to the maximum id in the table
    db.execute("""
        SELECT setval('teams_id_seq', (SELECT MAX(id) FROM teams));
    """)

def insert_csv_into_users(db, data):
    for row in data:
        db.execute(
            """
            INSERT INTO users (id, name, password, is_admin)
            VALUES (:id, :name, :password, :is_admin)
            ON CONFLICT (id) DO NOTHING
            """,
            {
                "id": row["id"],
                "name": row["name"],
                "password": row["password"],
                "is_admin": row["is_admin"],
            }
        )

    # Update the sequence to the maximum id in the table
    db.execute("""
        SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
    """)

def insert_csv_into_comments(db, data):
    for row in data:
        db.execute(
            """
            INSERT INTO comments (id, team_id, user_id, comment, created_at)
            VALUES (:id, :team_id, :user_id, :comment, :created_at)
            ON CONFLICT (id) DO NOTHING
            """,
            {
                "id": row["id"],
                "team_id": row["team_id"],
                "user_id": row["user_id"],
                "comment": row["comment"],
                "created_at": row["created_at"]
            }
        )

    # Update the sequence to the maximum id in the table
    db.execute("""
        SELECT setval('comments_id_seq', (SELECT MAX(id) FROM comments));
    """)


def check_for_admin(db, user_id):
    return db.query_value("""
        SELECT is_admin
        FROM users
        WHERE id = :user_id
        """, user_id=user_id)


def fetch_all_users(db):
    return db.query("""
        SELECT *
        FROM users
        """)


def get_team_from_id(db, team_id):
    return db.query_row("""
                SELECT *
                FROM teams
                WHERE id = :team_id
                """, team_id=team_id)
