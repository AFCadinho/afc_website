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
