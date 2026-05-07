import csv
import sqlite3
from io import StringIO

from collect_data_script import fetch_csv, format_date

DATA_URL = ("https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-"
            "5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6"
            "/download/violations.csv")


class Database:

    def __init__(self):  # Using persistent connection
        self.connection = sqlite3.connect('db/database.db',
                                          check_same_thread=False)
        # Enables concurrent access
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()

    def disconnect(self):
        self.connection.close()

    # Search by specifying column and a keyword
    def search_violations(self, search_by, search_value):
        query = f"SELECT * FROM violations WHERE {search_by} LIKE ?"
        results = self.cursor.execute(query,
                                      (f'%{search_value}%',)).fetchall()
        return results

    def get_violations_between_dates(self, start_date, end_date):
        query = """SELECT * FROM violations WHERE date BETWEEN ? and ?"""

        self.cursor.execute(query, (start_date, end_date))
        results = self.cursor.fetchall()
        return [dict(row) for row in results]

    def get_total_violations_by_establishment(self, start_date, end_date):
        query = """SELECT etablissement, COUNT(*) as total
                    FROM violations
                    WHERE date BETWEEN ? AND ?
                    GROUP BY etablissement
                    ORDER BY total DESC
                """
        self.cursor.execute(query, (start_date, end_date))
        results = self.cursor.fetchall()
        return [dict(row) for row in results]

    def get_violations_by_establishment(self, name):
        query = """SELECT * FROM violations WHERE etablissement = ?"""
        self.cursor.execute(query, (name,))
        results = self.cursor.fetchall()
        return [dict(row) for row in results]

    def get_all_establishment(self):
        query = """SELECT DISTINCT etablissement FROM violations
                    ORDER BY etablissement ASC
                """
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [row["etablissement"] for row in results]

    def get_existing_violations_id(self):
        self.cursor.execute("SELECT id_poursuite FROM violations")
        results = self.cursor.fetchall()
        return set(row[0] for row in results)

    def get_violation_by_id(self, violation_id):
        query = """SELECT * FROM violations WHERE id_poursuite = ?"""
        self.cursor.execute(query, (violation_id,))
        results = self.cursor.fetchone()
        return dict(results)

    def get_current_sum_violations(self):
        query = """SELECT etablissement, COUNT(*) as total
                    FROM violations
                    GROUP BY etablissement
                    ORDER BY total DESC"""
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return [dict(row) for row in results]

    def insert_into_inspections(self, etablissement, adresse, ville,
                                date_visite, nom_client, prenom_client,
                                description):
        self.cursor.execute(
            "INSERT INTO inspections (etablissement, adresse, ville,"
            "date_visite, nom_client, prenom_client, description)"
            "VALUES (?,?,?,?,?,?,?)",
            (etablissement, adresse, ville, date_visite, nom_client,
             prenom_client, description)
        )
        self.connection.commit()

    def delete_inspection_by_id(self, identifier):
        self.cursor.execute("DELETE FROM inspections WHERE id = ?",
                            (identifier,))
        self.connection.commit()
        return self.cursor.rowcount > 0


def insert_data_into_db(csv_data):
    db = Database()
    existing_ids = db.get_existing_violations_id()
    new_violations = []

    reader = csv.reader(StringIO(csv_data))
    next(reader)

    for row in reader:
        if int(row[0]) not in existing_ids:
            row[2] = format_date(row[2])
            row[5] = format_date(row[5])
            row[11] = format_date(row[11])
            db.cursor.execute(
                """INSERT INTO violations (
                    id_poursuite, business_id, date, description, adresse,
                    date_jugement, etablissement, montant, proprietaire, ville,
                    statut, date_statut, categorie)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                row
            )
            new_violations.append(db.get_violation_by_id(int(row[0])))

    db.connection.commit()
    db.disconnect()
    return new_violations


def update_database():
    csv_data = fetch_csv()
    new_violations = insert_data_into_db(csv_data)
    return new_violations
