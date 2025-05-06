-- 1) Total events:
SELECT COUNT(*) FROM Earthquakes;

-- 2) Top 5 quakes ever:
SELECT magnitude, place, event_time
  FROM Earthquakes
 ORDER BY magnitude DESC
 LIMIT 5;

-- 3) Quakes ≥ 6.0 in the last month:
SELECT * FROM Earthquakes
 WHERE magnitude >= 6.0
   AND event_time >= datetime('now', '-30 days');
