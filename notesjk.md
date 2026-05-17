## Notes
  1. Ξεκινάμε τον Flask server (το API)
  ```bash
   cd "/Users/johnkarelis/Documents/VS Code/Projects_general/PyCarGr"
  python pycargr/api.py
  Αυτό τρέχει τον server στο http://127.0.0.1:8080
  ```
  ---

2. Σε νέο terminal, καλούμε το API με τα params από το URL σου — αλλά μετατρέπουμε το car.gr URL σε API call:

  > Το car.gr URL:
  https://www.car.gr/classifieds/cars/?category=15001&condition=used&make=12522&make=13272...

```bash
  Γίνεται:
  curl "http://127.0.0.1:8080/api/search?category=15001&condition=used&make=12522&make=13272&make=13687&make=14093&make=32186&mileag
  e-to=70000&price-from=10000&price-to=17500&registration-from=2022&registration-to=2023"
  ```
  ---
## 3. Τι γίνεται internally:
  - Το API παίρνει τα params
  - Χτίζει ξανά το car.gr URL (SEARCH_BASE_URL + params)
  - Ο SearchResultPageParser κάνει scrape τη σελίδα και βρίσκει τα car IDs
  - Για κάθε αυτοκίνητο, ο CarItemParser επισκέπτεται το car.gr και παίρνει τα details
  - Επιστρέφει JSON

  Σημείωση: Θα πάρει αρκετή ώρα γιατί κάνει time.sleep(1) ανάμεσα σε κάθε αυτοκίνητο για να μην μπλοκαριστεί από το car.gr.
  ---
