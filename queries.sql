
-- Run these against earthquakes.db in sqlite3 or any SQLite GUI

-- 1) Total number of recorded earthquakes
SELECT COUNT(*) AS total_quakes
  FROM Earthquakes;

-- 2) Top 5 largest quakes ever recorded
SELECT magnitude, place, event_time
  FROM Earthquakes
 ORDER BY magnitude DESC
 LIMIT 5;

-- 3) Quakes of magnitude ≥ 6.0 in the last 30 days
SELECT magnitude, place, event_time
  FROM Earthquakes
 WHERE magnitude >= 6.0
   AND event_time >= datetime('now', '-30 days')
 ORDER BY magnitude DESC;

-- 4) All quakes in the past year, ordered newest first
SELECT *
  FROM Earthquakes
 WHERE event_time >= datetime('now', '-1 year')
 ORDER BY event_time DESC;

-- 5) Average depth by year
SELECT substr(event_time,1,4) AS year,
       ROUND(AVG(depth_km),2) AS avg_depth_km
  FROM Earthquakes
 GROUP BY year
 ORDER BY year DESC;
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
