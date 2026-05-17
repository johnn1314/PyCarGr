#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

import csv
from sqlite3 import connect
from urllib.parse import urlencode

from flask import Flask, jsonify, request, send_file

from pycargr import SEARCH_BASE_URL, init_db, save_car, DB_PATH
from pycargr.parser import parse_car_page, parse_search_results
from pycargr.model import to_dict

app = Flask(__name__)
app.json.ensure_ascii = False

init_db()


@app.route("/api/car/<car>", methods=["GET"])
def get_car(car):
    return jsonify(to_dict(parse_car_page(car)))


@app.route("/api/search", methods=["GET"])
def search():
    request_args = request.args.to_dict(flat=False)
    export_format = request_args.pop('format', ['json'])[0]

    search_url = SEARCH_BASE_URL + '?' + urlencode(request_args, doseq=True)

    results = list(parse_search_results(search_url))

    new_count = 0
    for car in results:
        with connect(str(DB_PATH)) as db:
            exists = db.execute("SELECT count(*) FROM cars WHERE id=?", (car.car_id,)).fetchone()[0]
        if not exists:
            save_car(car)
            new_count += 1
        else:
            save_car(car)  # UPDATE με νέα scraped_at

    print(f"[DB] {new_count} νέες αγγελίες, {len(results) - new_count} ανανεωμένες")

    if export_format == 'json':
        return jsonify(list(map(to_dict, results)))

    elif export_format == 'csv':
        with open(app.root_path + 'data.csv', 'w') as f:
            dicts = [to_dict(r) for r in results]
            writer = csv.DictWriter(f, fieldnames=dicts[0].keys())
            writer.writeheader()
            for d in dicts:
                d.pop('images', None)
                writer.writerow(d)
        return send_file(app.root_path + 'data.csv', as_attachment=True,
                         download_name='data.csv', mimetype='text/csv')

    else:
        return jsonify(error='Unsupported export format. Can only format=csv or format=json'), 400


@app.route("/api/db/cars", methods=["GET"])
def db_cars():
    """Επιστρέφει αποθηκευμένες αγγελίες από τη DB χωρίς scraping."""
    with connect(str(DB_PATH)) as db:
        db.row_factory = lambda c, r: dict(zip([col[0] for col in c.description], r))
        rows = db.execute("SELECT * FROM cars ORDER BY scraped_at DESC").fetchall()
    return jsonify(rows)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
