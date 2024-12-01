import pandas as pd
import queries
import csv

def create_csv_from_teams(db):
    rows = queries.get_all_teams_data(db)
    
    # data = [dict(row) for row in rows]
    data = []
    for row in rows:
        row_dict = dict(row)
        data.append(row_dict)
    
    csv_file_path = "teams.csv"

    df = pd.DataFrame(data)
    df.to_csv(csv_file_path, index=False)


def read_csv_to_dict(csv_file_path="teams.csv"):
    data = []
    with open(csv_file_path, mode="r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data.append(dict(row))
    return data