import pandas as pd
import queries
import csv

def create_csv_from_table(db, csv_file_paths, table_names):

    for num in range(len(csv_file_paths)):
    
        table_name = table_names[num]
        csv_file_path = csv_file_paths[num]
        rows = db.query(f"""
                SELECT *
                FROM {table_name}
                """)
        
        data = []
        for row in rows:
            row_dict = dict(row)
            data.append(row_dict)

        df = pd.DataFrame(data)
        df.to_csv(csv_file_path, index=False)


def read_csv_to_dict(csv_file_path):
    data = []
    with open(csv_file_path, mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data.append(dict(row))
    return data


def restore_teams_table(db, csv_file_paths):
    for file_path in csv_file_paths:
        data = read_csv_to_dict(file_path)

        if file_path == "csv/teams.csv":
            queries.insert_csv_into_teams(db, data)
        elif file_path == "csv/users.csv":
            queries.insert_csv_into_users(db, data)
        elif file_path == "csv/comments.csv":
            queries.insert_csv_into_comments(db, data)