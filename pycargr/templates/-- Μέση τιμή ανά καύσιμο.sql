  -- Μέση τιμή ανά καύσιμο
  SELECT fueltype, round(avg(price)) as avg_price, count(*) as cnt
  FROM cars WHERE price IS NOT NULL GROUP BY fueltype;