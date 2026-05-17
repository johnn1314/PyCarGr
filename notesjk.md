# PyCarGr — Cheatsheet

---

## Βήμα 1: Εκκίνηση server

```bash
cd "/Users/johnkarelis/Documents/VS Code/Projects_general/PyCarGr"
python pycargr/api.py
# → Flask server στο http://127.0.0.1:8080
```

---

## Βήμα 2: Τι γίνεται internally (σειρά εκτέλεσης)

```
curl "http://127.0.0.1:8080/api/search?make=12522&price-to=17500"
        │
        ▼
[Flask api.py] /api/search
  • Παίρνει τα params από το URL
  • Χτίζει το car.gr URL: SEARCH_BASE_URL + params
        │
        ▼
[parser.py] SearchResultPageParser(url)
  • Κάνει HTTP GET στο car.gr
  • Ψάχνει για <a class="row-anchor"> links
  • Εξάγει τα car IDs (π.χ. "54092453")
        │
        ▼  (για κάθε ID, με sleep(1) ανάμεσα)
[parser.py] CarItemParser(car_id)
  • Κάνει GET στο car.gr/<car_id>
  • Διαβάζει JSON-LD (<script type="application/ld+json">)
  • Διαβάζει feature-label / feature-value divs
  • Εξάγει: price, km, bhp, engine, color, fueltype, transmission, city, images κλπ
        │
        ▼
[model.py] Car object → to_dict()
        │
        ▼
Flask επιστρέφει JSON
```

---

## Βήμα 3: Βασικές εντολές

```bash
# Ένα συγκεκριμένο αυτοκίνητο (ID από το car.gr URL)
curl "http://127.0.0.1:8080/api/car/54092453"

# Search — copy-paste τα params από το car.gr URL
curl "http://127.0.0.1:8080/api/search?category=15001&condition=used&make=12522&make=13272&price-from=10000&price-to=17500&registration-from=2022"

# CSV export
curl "http://127.0.0.1:8080/api/search?make=12522&format=csv" -o cars.csv

# Pretty print JSON
curl "http://127.0.0.1:8080/api/search?make=12522" | python -m json.tool | head -50
```

---

## Παράμετροι car.gr που δουλεύουν ως φίλτρα

| Param | Τι κάνει |
|---|---|
| `make=12522` | Μάρκα (π.χ. Ford=12522, BMW=13272) |
| `price-from` / `price-to` | Εύρος τιμής (€) |
| `mileage-to` | Μέγιστα χιλιόμετρα |
| `registration-from/to` | Έτος κυκλοφορίας |
| `condition=used` | Μεταχειρισμένο |
| `category=15001` | Κατηγορία (επιβατικά) |
| `format=csv` | Εξαγωγή CSV (αντί JSON) |

---
---
---
---

## Ανανέωση βάσης (workflow)

**1. Ο server πρέπει να τρέχει:**
```bash
cd "/Users/johnkarelis/Documents/VS Code/Projects_general/PyCarGr"
python pycargr/api.py
```

**2. Τρέχεις το search με τα φίλτρα σου (μια φορά την ημέρα αρκεί):**
```bash
curl "http://127.0.0.1:8080/api/search?category=15001&condition=used&make=12522&make=13272&make=13687&make=14093&make=32186&mileage-to=70000&price-from=10000&price-to=17500&registration-from=2022&registration-to=2023"
```

Αυτόματα:
- Νέες αγγελίες → προστίθενται στη DB
- Υπάρχουσες → ανανεώνεται το `scraped_at`

**3. Βλέπεις τα δεδομένα:**
- SQLite Viewer στο VS Code → κάνεις 🔄 refresh στο `pycargr.db`
- Ή χωρίς scraping (instant): `curl "http://127.0.0.1:8080/api/db/cars"`

---

## Σημειώσεις

- Το search παίρνει ώρα (sleep 1s ανά αυτοκίνητο) — 20 αγγελίες ≈ 20 δευτερόλεπτα.
- Η DB βρίσκεται μέσα στο project: `pycargr.db`
- Το car.gr URL μετατρέπεται 1:1 σε API call — απλώς αλλάζεις το base URL.

---

## Παράδειγμα πλήρους search (από car.gr URL)

> car.gr URL:
> `https://www.car.gr/classifieds/cars/?category=15001&condition=used&make=12522&make=13272&make=13687&make=14093&make=32186&mileage-to=70000&price-from=10000&price-to=17500&registration-from=2022&registration-to=2023`

```bash
curl "http://127.0.0.1:8080/api/search?category=15001&condition=used&make=12522&make=13272&make=13687&make=14093&make=32186&mileage-to=70000&price-from=10000&price-to=17500&registration-from=2022&registration-to=2023"
```
