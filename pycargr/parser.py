#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

__author__ = 'Florents Tselai'

import json
import re
import time
from datetime import datetime
from urllib.request import urlopen, Request

from bs4 import BeautifulSoup

from pycargr.model import Car

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
}


class SearchResultPageParser:
    def __init__(self, search_page_url):
        self.search_page_url = search_page_url
        req = Request(search_page_url, data=None, headers=HEADERS)
        self.html = urlopen(req).read().decode('utf-8')
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.num_results = None
        for text in self.soup.find_all(string=lambda t: t and 'αγγελίες' in t):
            m = re.search(r'([0-9.]+)\s*αγγελίες', text)
            if m:
                self.num_results = int(m.group(1).replace('.', ''))
                break

    def parse(self):
        seen = set()
        for a in self.soup.find_all('a', class_='row-anchor'):
            href = a.get('href', '')
            if '/classifieds/cars/view/' not in href:
                continue
            car_id = href.split('/view/')[-1].split('-')[0].split('?')[0]
            if car_id.isdigit() and car_id not in seen:
                seen.add(car_id)
                yield car_id

    def __len__(self):
        return self.num_results


class CarItemParser:
    def __init__(self, car_id):
        self.car_id = car_id
        self.req = Request(
            'https://www.car.gr/%s' % self.car_id,
            data=None,
            headers=HEADERS,
        )
        self.html = urlopen(self.req).read().decode('utf-8')
        self.soup = BeautifulSoup(self.html, 'html.parser')

        self._ld_data = {}
        for script in self.soup.find_all('script', type='application/ld+json'):
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'Car':
                    self._ld_data = data
                    break
            except Exception:
                pass

        labels = self.soup.find_all('div', class_='feature-label')
        values = self.soup.find_all('div', class_='feature-value')
        self._features = {}
        for label, value in zip(labels, values):
            key = label.text.strip()
            if key not in self._features:
                self._features[key] = value.text.strip()

    def parse_km(self):
        try:
            return float(self._ld_data['mileageFromOdometer']['value'])
        except Exception:
            pass
        try:
            raw = self._features['Χιλιόμετρα']
            return float(raw.replace('.', '').replace('χλμ', '').strip())
        except Exception:
            return None

    def parse_bhp(self):
        try:
            raw = self._features['Ιπποδύναμη']
            return int(raw.replace('hp', '').replace('bhp', '').strip())
        except Exception:
            return None

    def parse_title(self):
        try:
            return self.soup.find('title').text
        except Exception:
            return None

    def parse_price(self):
        try:
            return float(self._ld_data['offers']['priceSpecification']['price'])
        except Exception:
            return None

    def parse_release_date(self):
        try:
            raw = self._features['Χρονολογία']  # e.g. '6 / 2011'
            return datetime.strptime(raw, '%m / %Y').strftime('%b %Y')
        except Exception:
            return None

    def parse_engine(self):
        try:
            raw = self._features['Κυβικά']  # e.g. '1.798 cc'
            return int(raw.replace('.', '').replace('cc', '').strip())
        except Exception:
            return None

    def parse_color(self):
        try:
            label = self.soup.find('div', string=lambda t: t and t.strip() == 'Χρώμα')
            return label.find_next_sibling('div').text.strip()
        except Exception:
            return None

    def parse_fueltype(self):
        try:
            return self._ld_data['fuelType']
        except Exception:
            return None

    def parse_description(self):
        try:
            return self.soup.find('div', class_='description').text.strip()
        except Exception:
            return None

    def _parse_location(self):
        for span in self.soup.find_all('span', class_='tw-gap-1'):
            text = span.text.strip()
            if re.search(r'\d{5}$', text) and 'car.gr' not in text:
                return text
        return None

    def parse_city(self):
        try:
            loc = self._parse_location()
            if loc:
                m = re.search(r'\d{4,5}$', loc)
                return loc[:m.start()].strip() if m else loc
        except Exception:
            return None

    def parse_region(self):
        return None

    def parse_postal_code(self):
        try:
            loc = self._parse_location()
            if loc:
                m = re.search(r'(\d{4,5})$', loc)
                if m:
                    return int(m.group(1))
        except Exception:
            return None

    def parse_transmission(self):
        try:
            return self._ld_data['vehicleTransmission']
        except Exception:
            return None

    def parse_images(self):
        try:
            return self._ld_data.get('image', [])
        except Exception:
            return None

    def parse(self):
        c = Car(self.car_id)
        c.title = self.parse_title()
        c.price = self.parse_price()
        c.release_date = self.parse_release_date()
        c.engine = self.parse_engine()
        c.km = self.parse_km()
        c.bhp = self.parse_bhp()
        c.url = self.req.full_url
        c.color = self.parse_color()
        c.fueltype = self.parse_fueltype()
        c.description = self.parse_description()
        c.city = self.parse_city()
        c.region = self.parse_region()
        c.postal_code = self.parse_postal_code()
        c.transmission = self.parse_transmission()
        c.images = self.parse_images()
        c.html = self.html
        c.scraped_at = datetime.now().isoformat()
        return c


# Utility methods
def parse_search_results(search_url):
    car_ids = SearchResultPageParser(search_url).parse()
    for car_id in car_ids:
        time.sleep(1)
        yield parse_car_page(car_id)


def parse_car_page(car_id):
    car = CarItemParser(car_id).parse()
    return car
