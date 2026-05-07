import json

import requests
from flask import Flask, render_template, request, redirect, url_for, g, \
    request, jsonify, Response

import sqlite3
from database import Database, update_database
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import xml.etree.ElementTree as ET
import csv
import io
from jsonschema import validate, ValidationError
from utils.email_utils import notify_by_email

app = Flask(__name__)

inspection_schema = {
    "type": "object",
    "properties": {
        "etablissement": {"type": "string"},
        "adresse": {"type": "string"},
        "ville": {"type": "string"},
        "date_visite": {"type": "string", "format": "date"},
        "nom_client": {"type": "string"},
        "prenom_client": {"type": "string"},
        "description": {"type": "string"}
    },
    "required": ["etablissement", "adresse", "ville", "date_visite",
                 "nom_client", "prenom_client", "description"]
}


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


@app.route('/', methods=['GET', 'POST'])
def index():
    results = []

    if request.method == 'POST':
        form_data = {
            'search_by': request.form.get('search_by'),
            'search_value': request.form.get('search_value')
        }

        db = Database()
        results = db.search_violations(form_data['search_by'],
                                       form_data['search_value'])
        db.disconnect()
        return render_template('results_violations.html',
                               results=results), 200
    db = Database()
    restaurant_names = db.get_all_establishment()
    db.disconnect()
    return render_template('index.html',
                           restaurant_names=restaurant_names), 200


# A4, A5
@app.route('/contrevenants', methods=['GET'])
def get_violations_by_date():
    du = request.args.get('du')
    au = request.args.get('au')
    # optional param to switch between A4 & A5
    summary = request.args.get('sum')

    try:
        start_date = datetime.strptime(du, "%Y-%m-%d").date()
        end_date = datetime.strptime(au, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify({"error": "Paramètres de dates invalides."
                                 "Format attendu: YYYY-MM-DD"}), 400

    db = Database()
    if summary and summary.lower() == 'true':
        results = db.get_total_violations_by_establishment(start_date,
                                                           end_date)
    else:
        results = db.get_violations_between_dates(start_date, end_date)
    db.disconnect()

    return Response(
        json.dumps(results, ensure_ascii=False, indent=2),
        content_type='application/json; charset=utf-8'
    ), 200


@app.route('/doc')
def api_documentation():
    try:
        with open('docs/docs.html', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return "<h1>La documentation Raml n'a pas encore été généré.<h1>", 400


@app.route("/contrevenants/etablissement", methods=['GET'])
def get_violations_by_establishment():
    name = request.args.get('nom')

    if not name:
        return jsonify({"erreur:" "Paramètre <nom> maquant."}), 400

    db = Database()
    results = db.get_violations_by_establishment(name)
    db.disconnect()

    if not results:
        return jsonify({"erreur:" "Aucune contraventions trouvée pour cet"
                        "établissement."}), 404

    return jsonify(results), 200


@app.route('/contrevenants/total-violations', methods=['GET'])
def get_total_violations():
    db = Database()
    results = db.get_current_sum_violations()
    db.disconnect()

    if request.args.get('format') == 'xml':
        root = ET.Element('violations')
        for item in results:
            entry = ET.SubElement(root, 'etablissement')
            ET.SubElement(entry, 'nom').text = item['etablissement']
            ET.SubElement(entry, 'total').text = str(item['total'])
        xml_data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
        return Response(xml_data, mimetype='application/xml')

    if request.args.get('format') == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['etablissement', 'total'])
        for item in results:
            writer.writerow([item['etablissement'], item['total']])
        csv_data = output.getvalue()
        return Response(csv_data, mimetype='text/csv')

    return jsonify(results), 200


# D1
@app.route('/inspection-form', methods=['GET'])
def show_inspection_form():
    return render_template('demand-inspection.html')


@app.route('/demand-inspection', methods=['POST'])
def demand_establishment_inspection():
    data = request.get_json()

    try:
        validate(instance=data, schema=inspection_schema)
    except ValidationError as e:
        return jsonify({"erreur": "Demande d'inspection invalide.",
                        "détails": str(e)}), 400

    db = Database()
    db.insert_into_inspections(
        data['etablissement'],
        data['adresse'],
        data['ville'],
        data['date_visite'],
        data['nom_client'],
        data['prenom_client'],
        data['description']
    )
    db.disconnect()
    return jsonify({"message": "Demande d'inspection reçu."}), 201


@app.route("/demand-inspection/<int:identifier>", methods=["DELETE"])
def delete_inspection(identifier):
    db = Database()
    deleted = db.delete_inspection_by_id(identifier)
    db.disconnect()

    if deleted:
        return jsonify(
            {"message": f"Demande d'inspection"
                        f"#{identifier} supprimée avec succès."}), 200
    else:
        return jsonify({"error": "Demande d'inspection introuvable."}), 404


def scheduled_job():
    new_violations = update_database()
    if new_violations:
        notify_by_email(new_violations)
        print(f"{len(new_violations)} new violations inserted.")
    else:
        print("No new violations to report.")


scheduler = BackgroundScheduler()
scheduler.add_job(func=scheduled_job, trigger='cron', hour=0, minute=0)
# scheduler.add_job(func=scheduled_job, trigger='interval', minutes=5)
scheduler.start()


if __name__ == '__main__':
    app.run()
