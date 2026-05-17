from json import dumps
from pathlib import Path
from sqlite3 import connect

from pycargr.model import Car

DB_PATH = Path(__file__).parent.parent / 'pycargr.db'
SCHEMA_PATH = Path(__file__).parent.parent / 'schema.sql'

SEARCH_BASE_URL = 'https://www.car.gr/classifieds/cars/'


def init_db():
    with connect(str(DB_PATH)) as db:
        db.executescript(SCHEMA_PATH.read_text())


def save_car(*cars):
    car_data = [(c.car_id, c.title, c.price, c.release_date, c.km, c.bhp, c.url, c.color, c.fueltype,
                 c.description, c.city, c.region, c.postal_code, c.transmission, dumps(c.images or []), None,
                 c.scraped_at) for c in cars]
    with connect(str(DB_PATH), timeout=10) as db:
        db.executemany("INSERT OR REPLACE INTO cars VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       car_data)
