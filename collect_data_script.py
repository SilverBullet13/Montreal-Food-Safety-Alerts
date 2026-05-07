import requests
import sqlite3
import csv
from io import StringIO
from datetime import datetime

DATA_URL = ("https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-"
            "5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6"
            "/download/violations.csv")


def format_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        return date_str  # Returns the date string as is


def fetch_csv():
    response = requests.get(DATA_URL)
    response.raise_for_status()
    return response.content.decode("utf-8")


def insert_data_into_db(csv_data):
    connection = sqlite3.connect('db/database.db')
    #connection.text_factory = lambda x: x.decode("utf-8", "ignore")
    cursor = connection.cursor()
    reader = csv.reader(StringIO(csv_data))     # Returns a list
    next(reader)  # skip header row

    for row in reader:
        row[2] = format_date(row[2])
        row[5] = format_date(row[5])
        row[11] = format_date(row[11])
        cursor.execute(
            """INSERT INTO violations (
                id_poursuite, business_id, date, description, adresse,
                date_jugement, etablissement, montant, proprietaire, ville,
                statut, date_statut, categorie)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            row
        )

    connection.commit()
    connection.close()


def main():
    csv_data = fetch_csv()
    insert_data_into_db(csv_data)
    print("Data successfully inserted.")


if __name__ == "__main__":
    main()
